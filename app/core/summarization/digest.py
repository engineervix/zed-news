import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import TypeVar

import dspy

from app.core.db.models import Article
from app.core.summarization.corroboration import EXA_API_KEY, exa_search
from app.core.summarization.retrieval import find_related_articles
from app.core.utilities import DATA_DIR, truncate

CANONICAL_SECTIONS = ("## Main Stories", "## Other Notable Stories", "## Key Takeaways & Watchpoints")
# Shorter than news/digest.py's 2200-char main-article clip - this is supplementary
# framing context, not primary content, and may include several matches per article.
RELATED_CONTEXT_EXCERPT_LENGTH = 500
EVAL_ARTICLES_PATH = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "eval_articles.json"
# Hand-authored, not scraped - unlike eval_articles.json/eval_digests.json (gitignored real
# content, regenerate locally), this is synthetic and committed: BootstrapFewShot needs at
# least one case per continuity scenario to ever bootstrap a demo exercising related_context.
CONTINUITY_EVAL_PATH = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "eval_continuity.json"
# Real find_related_articles matches for eval_articles.json, keyed by article url - built
# against the live DB (see fetch_eval_continuity_context.py). Gitignored, same policy as
# eval_articles.json/eval_digests.json: real content, regenerate locally.
EVAL_CONTINUITY_CONTEXT_PATH = (
    Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "eval_continuity_context.json"
)
COMPILED_PROGRAM_PATH = DATA_DIR / "optimized_digest_program.json"
# Padding around a matched topic's real date span for the Exa corroboration search window,
# so the exact match date itself isn't clipped by an exclusive/inclusive boundary edge case.
CORROBORATION_LOOKBACK_BUFFER_DAYS = 3

# Shared with post.py and eleventify.py: their signatures
# all take a generated digest (not raw articles) as input, so they build their eval
# sets from real digests generated here rather than duplicating this path per module.
EVAL_DIGESTS_PATH = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "eval_digests.json"

ModuleT = TypeVar("ModuleT", bound=dspy.Module)


@dataclass
class Digest:
    """A generated news digest, along with the source articles it covers."""

    content: str
    total_articles: int
    sources: list[str]


class DigestSignature(dspy.Signature):
    """Write a Zambian news digest in Markdown from the given articles.

    Adopt the voice of a patriotic Zambian news editor with a watchdog streak: professional
    and engaging, but with sharp critical scrutiny. Question motives, and call out spin, gaps,
    or contradictions in the reporting itself, pressing on accountability wherever officials or
    institutions are involved. Where appropriate, and only for less serious topics, use dry,
    subtle Zambian wit - never on crime, accidents, or political tensions. Stay grounded in what
    the input actually says; critical framing must never invent suspicion beyond the facts given.
    """

    articles: str = dspy.InputField(desc="Numbered list of articles with title, source, and content")
    related_context: str = dspy.InputField(
        desc=(
            "Past coverage of a similar or recurring story, if any, each prefixed with how long "
            "ago it ran (e.g. '12 days ago', '6 months ago'). Empty when there is none - do not "
            "invent continuity that isn't given here. These are the nearest past matches by topic "
            "similarity, not guaranteed to be genuinely related - if an entry isn't actually about "
            "the same story or a real recurring pattern, ignore it rather than forcing a connection. "
            "For a genuine match, tie framing language to the actual gap stated: only call something "
            "a recent follow-up (e.g. 'as flagged last week...') when the gap given is genuinely "
            "short; for an old match, frame it as a recurring pattern (e.g. 'the fourth time this "
            "year...') rather than implying it just happened."
        )
    )
    digest: str = dspy.OutputField(
        desc=(
            "Markdown digest with exactly three level-2 headings, in this order and this exact "
            "wording: `## Main Stories`, `## Other Notable Stories`, `## Key Takeaways & "
            "Watchpoints` (two `#` characters, not three, and no other headings anywhere). Start "
            "directly with the intro paragraph, with no title heading. "
            "Main Stories: a numbered list - `1. **Title**` followed by 1-2 sentences per item, "
            "flagging any unverified claims, missing timelines, or gaps in the reporting. Other "
            "Notable Stories: grouped under bold category labels (e.g. `**Sports:**`) with `*` "
            "bullets beneath each. Key Takeaways & Watchpoints: 2-3 forward-looking, fact-based "
            "bullets naming what to watch for accountability (a deadline, a promised report, a "
            "follow-up vote)."
        )
    )


class DigestGenerator(dspy.Module):
    """DSPy module that generates a digest from formatted article text."""

    def __init__(self) -> None:
        super().__init__()
        self.generate = dspy.Predict(DigestSignature)

    def forward(self, articles: str, related_context: str = "") -> dspy.Prediction:
        return self.generate(articles=articles, related_context=related_context)


def _format_articles(articles: list[dict[str, str]]) -> str:
    lines = []
    for i, article in enumerate(articles, start=1):
        lines.append(f"{i}. {article['title']} (source: {article['source']})")
        lines.append(article["content"])
        lines.append("")
    return "\n".join(lines)


def format_elapsed(article_date: date, reference_date: date) -> str:
    """Describe the gap between `article_date` and `reference_date` in human terms.

    Deliberately approximate (30-day months, 365-day years) - this feeds a framing
    instruction to the LLM, not an accounting calculation.
    """
    days = max((reference_date - article_date).days, 0)
    if days == 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 7:
        return f"{days} days ago"
    if days < 30:
        weeks = days // 7
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    if days < 365:
        months = days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    years = days // 365
    return f"{years} year{'s' if years != 1 else ''} ago"


def format_related_context(matches: list[dict], reference_date: date) -> str:
    """Format `find_related_articles` matches into `DigestSignature`'s `related_context` input.

    Each match is prefixed with its elapsed time relative to `reference_date` - a guard
    against misframing an old match as recent: the model is told the real gap and must
    frame accordingly, not just given the content.
    """
    if not matches:
        return ""

    lines = []
    for match in matches:
        excerpt = truncate(match["content"].strip(), RELATED_CONTEXT_EXCERPT_LENGTH)
        elapsed = format_elapsed(match["date"], reference_date)
        lines.append(f"- {elapsed}: {match['title']}\n  {excerpt}")
    return "\n".join(lines)


def build_related_context(articles_with_matches: list[tuple[dict[str, str], list[dict]]], reference_date: date) -> str:
    """Combine each article's related past matches into one `related_context` block.

    Matches dated `reference_date` or later are dropped - those are other articles from
    today's own batch, already present in the main `articles` input, so treating them as
    "related context" would just duplicate today's own digest content rather than surface
    real continuity. Only articles with at least one genuinely past match are included,
    each labelled with its title so the model can attach a continuity claim to the right
    story. Returns "" when nothing qualifies.
    """
    blocks = []
    for article, matches in articles_with_matches:
        past_matches = [match for match in matches if match["date"] < reference_date]
        formatted = format_related_context(past_matches, reference_date)
        if formatted:
            blocks.append(f'Regarding "{article["title"]}":\n{formatted}')
    return "\n\n".join(blocks)


def gather_related_context(
    news: list[dict[str, str]], saved_articles: Mapping[str, Article], reference_date: date
) -> str:
    """Look up each article's related past coverage and format it into one `related_context` block.

    An article whose URL isn't in `saved_articles` (e.g. not yet saved to the DB) is skipped -
    its DB row is where the embedding retrieval runs against lives. See `find_related_articles`
    for the lookup itself and `build_related_context` for how matches are filtered and formatted.
    """
    articles_with_matches = [
        (article, find_related_articles(saved_articles[article["url"]], reference_date=reference_date))
        for article in news
        if article["url"] in saved_articles
    ]
    return build_related_context(articles_with_matches, reference_date)


def generate_digest(articles: list[dict[str, str]], related_context: str = "") -> Digest | None:
    """Generate a news digest from articles using a DSPy module."""

    if not articles:
        return None

    prediction = DigestGenerator()(articles=_format_articles(articles), related_context=related_context)

    return Digest(
        content=prediction.digest,
        total_articles=len(articles),
        sources=[article["source"] for article in articles],
    )


def has_canonical_sections(text: str) -> bool:
    """Check that the three required section headings appear, in order, with no extras."""
    headings = re.findall(r"^## .+$", text, re.MULTILINE)
    return tuple(heading.rstrip() for heading in headings) == CANONICAL_SECTIONS


def has_intro_paragraph(text: str) -> bool:
    """Check that there is introductory text before the first section heading."""
    before_first_heading = text.split("## ", 1)[0]
    return bool(before_first_heading.strip())


def has_markdown_links(text: str) -> bool:
    """Check for markdown links, which the digest must not contain."""
    return bool(re.search(r"\[[^\]]+\]\([^)]+\)", text))


def has_html(text: str) -> bool:
    """Check for HTML tags, which the digest must not contain."""
    return bool(re.search(r"<[a-zA-Z][^>]*>", text))


def has_why_this_matters_label(text: str) -> bool:
    """Check for a 'Why this matters' label, which must stay woven into the prose instead."""
    return bool(re.search(r"why this matters", text, re.IGNORECASE))


def has_title_heading(text: str) -> bool:
    """Check for a single-hash title heading, which the digest must not contain."""
    return bool(re.search(r"^#(?!#)\s", text, re.MULTILINE))


def _extract_section(text: str, heading: str, next_heading: str | None) -> str:
    """Return the text between `heading` and `next_heading` (or end of text if None/absent)."""
    if heading not in text:
        return ""
    remainder = text[text.index(heading) + len(heading) :]
    if next_heading and next_heading in remainder:
        return remainder[: remainder.index(next_heading)]
    return remainder


def has_numbered_main_stories(text: str) -> bool:
    """Check that Main Stories items use a numbered list layout (e.g. '1. **Title**')."""
    section = _extract_section(text, "## Main Stories", "## Other Notable Stories")
    return bool(re.search(r"^\d+\.\s", section, re.MULTILINE))


def has_category_grouped_other_stories(text: str) -> bool:
    """Check that Other Notable Stories groups items under bold category labels."""
    section = _extract_section(text, "## Other Notable Stories", "## Key Takeaways & Watchpoints")
    return bool(re.search(r"^\*\*[^*\n]+:\*\*", section, re.MULTILINE))


COMPLIANCE_RULES: dict[str, Callable[[str], bool]] = {
    "canonical_sections": has_canonical_sections,
    "intro_paragraph": has_intro_paragraph,
    "no_markdown_links": lambda text: not has_markdown_links(text),
    "no_html": lambda text: not has_html(text),
    "no_why_this_matters": lambda text: not has_why_this_matters_label(text),
    "no_title_heading": lambda text: not has_title_heading(text),
    "numbered_main_stories": has_numbered_main_stories,
    "category_grouped_other_stories": has_category_grouped_other_stories,
}


def compliance_score(rules: dict[str, Callable[[str], bool]], text: str) -> float:
    """Score text against a dict of compliance rules, as a fraction in [0, 1].

    Shared by every `*_compliance_score` metric in this package (digest, Facebook
    post, image concept, digest description) - they differ only in which rules
    dict and which prediction field they check.
    """
    checks = [check(text) for check in rules.values()]
    return sum(checks) / len(checks)


def digest_compliance_score(example, pred, trace=None) -> float:
    """Score a generated digest against the hard formatting rules, as a fraction in [0, 1].

    Args:
        example: Unused. Accepted for compatibility with DSPy's metric signature.
        pred: A prediction with a `digest` field holding the generated Markdown.
        trace: Unused. Accepted for compatibility with DSPy's metric signature.

    Returns:
        The fraction of `COMPLIANCE_RULES` the digest passes, from 0.0 to 1.0.
    """
    return compliance_score(COMPLIANCE_RULES, pred.digest)


def load_eval_articles() -> list[dict[str, str]]:
    """Load the real articles fetched for building the optimizer eval set."""
    return json.loads(EVAL_ARTICLES_PATH.read_text())


def build_eval_set(articles: list[dict[str, str]], batch_size: int = 6) -> list[dspy.Example]:
    """Split articles into batches, each a DSPy example for optimization/eval."""
    batches = [articles[i : i + batch_size] for i in range(0, len(articles), batch_size)]
    return [dspy.Example(articles=_format_articles(batch)).with_inputs("articles") for batch in batches]


def load_continuity_eval_cases() -> list[dict]:
    """Load the hand-authored story-continuity eval cases.

    Each case is `{"case": str, "articles": [...same shape as eval_articles.json...],
    "matches": [{"article_title": str, "title": str, "content": str, "days_ago": int}]}`.
    `article_title` must exactly match one of the case's own `articles[].title` -
    `build_continuity_eval_set` asserts this so a typo or later title edit fails loudly
    instead of silently dropping the match.
    """
    return json.loads(CONTINUITY_EVAL_PATH.read_text())


def build_continuity_eval_set(cases: list[dict], reference_date: date) -> list[dspy.Example]:
    """Turn `load_continuity_eval_cases` output into DSPy examples with `related_context` filled in.

    One example per case, both `articles` and `related_context` marked as inputs - unlike
    `build_eval_set`'s plain batches, these exist specifically to give BootstrapFewShot (and a
    human eyeballing the output) something that exercises continuity framing. Each case's
    matches are dated relative to `reference_date` via `days_ago` rather than a fixed calendar
    date, so the elapsed-time framing this tests stays correct no matter when eval runs.
    """
    examples = []
    for case in cases:
        article_titles = {article["title"] for article in case["articles"]}
        for match in case["matches"]:
            assert match["article_title"] in article_titles, (
                f"eval_continuity.json case {case['case']!r}: match references unknown article "
                f"{match['article_title']!r}"
            )

        articles_with_matches = [
            (
                article,
                [
                    {
                        "title": match["title"],
                        "content": match["content"],
                        "date": reference_date - timedelta(days=match["days_ago"]),
                    }
                    for match in case["matches"]
                    if match["article_title"] == article["title"]
                ],
            )
            for article in case["articles"]
        ]
        related_context = build_related_context(articles_with_matches, reference_date)
        example = dspy.Example(
            articles=_format_articles(case["articles"]), related_context=related_context
        ).with_inputs("articles", "related_context")
        examples.append(example)
    return examples


def load_eval_continuity_context() -> dict[str, list[dict]]:
    """Load real `find_related_articles` matches for `eval_articles.json`, keyed by article url.

    An article missing from this map, or present with an empty list, has no real past match.
    """
    raw = json.loads(EVAL_CONTINUITY_CONTEXT_PATH.read_text())
    return {
        url: [{**match, "date": date.fromisoformat(match["date"])} for match in matches] for url, matches in raw.items()
    }


def build_real_continuity_eval_set(
    articles: list[dict[str, str]],
    context: dict[str, list[dict]],
    reference_date: date,
    batch_size: int = 18,
) -> list[dspy.Example]:
    """Batch real eval articles the same way as `build_eval_set`, attaching each batch's
    real `find_related_articles` matches (from `load_eval_continuity_context`) as
    `related_context`.

    Unlike the synthetic `eval_continuity.json` cases, these matches are real past coverage
    from the live DB - what makes `exa_corroboration_score` meaningful: a claim about
    fictional content can't be checked against the real web, only a claim about real
    coverage can. Batches with no real match anywhere are dropped, nothing to exercise.
    Each example also carries a non-input `continuity_topic` field - the first matched
    article's title and real match dates, the one `exa_corroboration_score` checks - kept
    structured rather than making the metric re-parse the formatted `related_context` string.
    """
    batches = [articles[i : i + batch_size] for i in range(0, len(articles), batch_size)]
    examples = []
    for batch in batches:
        articles_with_matches = [
            (article, [match for match in context.get(article["url"], []) if match["date"] < reference_date])
            for article in batch
        ]
        related_context = build_related_context(articles_with_matches, reference_date)
        if not related_context:
            continue
        # ponytail: one topic per batch (one Exa call per example, real cost), not every
        # matched article - upgrade to scoring every match and averaging if a single
        # representative topic proves too noisy against real data.
        continuity_topic = next(
            (
                {"title": article["title"], "dates": [match["date"] for match in matches]}
                for article, matches in articles_with_matches
                if matches
            ),
            None,
        )
        example = dspy.Example(
            articles=_format_articles(batch), related_context=related_context, continuity_topic=continuity_topic
        ).with_inputs("articles", "related_context")
        examples.append(example)
    return examples


def exa_corroboration_score(example, pred, trace=None) -> float | None:
    """Score whether an example's real continuity topic is independently corroborated on
    the real web, via one Exa search - an eval-time-only guard against a spurious embedding
    match masquerading as a real recurring story (see `build_real_continuity_eval_set`).

    Args:
        example: An example built by `build_real_continuity_eval_set`, carrying a
            `continuity_topic` field. Examples without one (e.g. from `build_eval_set` or
            the synthetic `build_continuity_eval_set`) score 1.0 - nothing to check, not a
            failure.
        pred: Unused - this checks the retrieved input the model was given, not what it
            wrote, since there's no reliable way to parse "was this claim about topic X"
            out of free-form generated prose.
        trace: Unused. Accepted for compatibility with DSPy's metric signature.

    Returns:
        1.0 if there is no continuity topic to check, or Exa independently returns at
        least one result inside the topic's real date span; 0.0 if it returns none.
        None when `EXA_API_KEY` isn't configured - nothing was actually checked, so
        callers must exclude it from an average rather than counting it as a failure.
    """
    topic = getattr(example, "continuity_topic", None)
    if not topic:
        return 1.0
    if not EXA_API_KEY:
        return None

    buffer = timedelta(days=CORROBORATION_LOOKBACK_BUFFER_DAYS)
    results = exa_search(topic["title"], min(topic["dates"]) - buffer, max(topic["dates"]) + buffer)
    return 1.0 if results else 0.0


class ContinuityFaithfulnessJudge(dspy.Signature):
    """Judge whether a generated news digest's story-continuity framing, if any, is
    faithful to the related_context it was given - not fabricated, not misdated relative
    to the real elapsed time stated, and not forcing a connection to unrelated content.
    """

    related_context: str = dspy.InputField(
        desc="Past coverage the digest generator was given, each match prefixed with its real elapsed time"
    )
    digest: str = dspy.InputField(desc="The generated news digest to check")
    faithful: bool = dspy.OutputField(
        desc="True if the digest makes no continuity claim, or makes one that accurately reflects the "
        "elapsed time and content given in related_context. False if it fabricates a connection not "
        "supported by related_context, or states a wrong/misleading elapsed time."
    )


def continuity_faithfulness_score(example, pred, trace=None) -> float:
    """Score whether a generated digest's continuity framing (if any) is faithful to the
    related_context it was given, via one LLM-judge call - an eval-time-only guard against
    the model fabricating a connection or misstating how long ago a match ran.

    Args:
        example: An example carrying a `related_context` field (e.g. from
            `build_continuity_eval_set` or `build_real_continuity_eval_set`). Examples
            with an empty `related_context` score 1.0 without calling the judge - nothing
            to fabricate.
        pred: A prediction with a `digest` field holding the generated Markdown to check.
        trace: Unused. Accepted for compatibility with DSPy's metric signature.

    Returns:
        1.0 if there is no related_context to check, or the judge finds the digest
        faithful to it; 0.0 otherwise.
    """
    related_context = getattr(example, "related_context", "")
    if not related_context:
        return 1.0

    # ChainOfThought, not bare Predict: verified against a real failure - DeepSeek-V4-Flash
    # answered False with no reasoning step on a digest that made no continuity claim at all
    # (should be True per the signature's own rule), then correctly answered True once asked
    # to reason first. A bare bool judgment on this kind of "is X faithful to Y" question is
    # unreliable without it.
    judge = dspy.ChainOfThought(ContinuityFaithfulnessJudge)
    verdict = judge(related_context=related_context, digest=pred.digest)
    return 1.0 if verdict.faithful else 0.0


def load_compiled(module_cls: type[ModuleT], path: Path) -> ModuleT:
    """Load a module class's optimizer-compiled program, if one has been synced to this machine.

    Falls back to the raw, unoptimized module when `path` does not exist - compiled
    programs embed real generated content in their few-shot demos, so none of them
    are committed to git. Deploys that want the optimized version must sync the file
    there themselves (see PLAN.md). Shared by every `load_compiled_*_generator` in
    this package.
    """
    module = module_cls()
    if path.exists():
        module.load(str(path))
    return module


def load_compiled_digest_generator() -> DigestGenerator:
    """Load the optimizer-compiled digest generator, if one has been synced to this machine.

    Falls back to the raw, unoptimized module when `COMPILED_PROGRAM_PATH` does not
    exist - the compiled program embeds real article content in its few-shot demos, so
    it is not committed to git. Deploys that want the optimized version must sync the
    file there themselves (see PLAN.md).
    """
    return load_compiled(DigestGenerator, COMPILED_PROGRAM_PATH)


def generate_digest_markdown(formatted_articles: str, related_context: str = "") -> str:
    """Generate digest Markdown from already-formatted article text.

    Args:
        formatted_articles: Article text as built by `_format_articles`, or an
            equivalent caller-built numbered list (see `create_news_digest`).
        related_context: Past coverage of a similar/recurring story, as built by
            `format_related_context`. Empty string when there is none.

    Returns:
        The generated Markdown digest.
    """
    return load_compiled_digest_generator()(articles=formatted_articles, related_context=related_context).digest
