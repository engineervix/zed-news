import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

import dspy

from app.core.utilities import DATA_DIR

CANONICAL_SECTIONS = ("## Main Stories", "## Other Notable Stories", "## Key Takeaways & Watchpoints")
EVAL_ARTICLES_PATH = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "eval_articles.json"
COMPILED_PROGRAM_PATH = DATA_DIR / "optimized_digest_program.json"

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
    digest: str = dspy.OutputField(
        desc=(
            "Markdown digest with Main Stories, Other Notable Stories, and Key Takeaways & "
            "Watchpoints sections. Start directly with the intro paragraph, with no title heading. "
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

    def forward(self, articles: str) -> dspy.Prediction:
        return self.generate(articles=articles)


def _format_articles(articles: list[dict[str, str]]) -> str:
    lines = []
    for i, article in enumerate(articles, start=1):
        lines.append(f"{i}. {article['title']} (source: {article['source']})")
        lines.append(article["content"])
        lines.append("")
    return "\n".join(lines)


def generate_digest(articles: list[dict[str, str]]) -> Digest | None:
    """Generate a news digest from articles using a DSPy module."""

    if not articles:
        return None

    prediction = DigestGenerator()(articles=_format_articles(articles))

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


def generate_digest_markdown(formatted_articles: str) -> str:
    """Generate digest Markdown from already-formatted article text.

    Args:
        formatted_articles: Article text as built by `_format_articles`, or an
            equivalent caller-built numbered list (see `create_news_digest`).

    Returns:
        The generated Markdown digest.
    """
    return load_compiled_digest_generator()(articles=formatted_articles).digest
