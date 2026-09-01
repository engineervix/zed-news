import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import dspy

from app.core.utilities import DATA_DIR

CANONICAL_SECTIONS = ("## Main Stories", "## Other Notable Stories", "## Key Takeaways & Watchpoints")
EVAL_ARTICLES_PATH = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "eval_articles.json"
COMPILED_PROGRAM_PATH = DATA_DIR / "optimized_digest_program.json"


@dataclass
class Digest:
    """A generated news digest, along with the source articles it covers."""

    content: str
    total_articles: int
    sources: list[str]


class DigestSignature(dspy.Signature):
    """Write a Zambian news digest in Markdown from the given articles."""

    articles: str = dspy.InputField(desc="Numbered list of articles with title, source, and content")
    digest: str = dspy.OutputField(
        desc=(
            "Markdown digest with Main Stories, Other Notable Stories, and Key Takeaways & "
            "Watchpoints sections. Start directly with the intro paragraph, with no title heading."
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


COMPLIANCE_RULES: dict[str, Callable[[str], bool]] = {
    "canonical_sections": has_canonical_sections,
    "intro_paragraph": has_intro_paragraph,
    "no_markdown_links": lambda text: not has_markdown_links(text),
    "no_html": lambda text: not has_html(text),
    "no_why_this_matters": lambda text: not has_why_this_matters_label(text),
    "no_title_heading": lambda text: not has_title_heading(text),
}


def digest_compliance_score(example, pred, trace=None) -> float:
    """Score a generated digest against the hard formatting rules, as a fraction in [0, 1].

    Args:
        example: Unused. Accepted for compatibility with DSPy's metric signature.
        pred: A prediction with a `digest` field holding the generated Markdown.
        trace: Unused. Accepted for compatibility with DSPy's metric signature.

    Returns:
        The fraction of `COMPLIANCE_RULES` the digest passes, from 0.0 to 1.0.
    """
    text = pred.digest
    checks = [check(text) for check in COMPLIANCE_RULES.values()]
    return sum(checks) / len(checks)


def load_eval_articles() -> list[dict[str, str]]:
    """Load the real articles fetched for building the optimizer eval set."""
    return json.loads(EVAL_ARTICLES_PATH.read_text())


def build_eval_set(articles: list[dict[str, str]], batch_size: int = 6) -> list[dspy.Example]:
    """Split articles into batches, each a DSPy example for optimization/eval."""
    batches = [articles[i : i + batch_size] for i in range(0, len(articles), batch_size)]
    return [dspy.Example(articles=_format_articles(batch)).with_inputs("articles") for batch in batches]


def load_compiled_digest_generator() -> DigestGenerator:
    """Load the optimizer-compiled digest generator, if one has been synced to this machine.

    Falls back to the raw, unoptimized module when `COMPILED_PROGRAM_PATH` does not
    exist - the compiled program embeds real article content in its few-shot demos, so
    it is not committed to git. Deploys that want the optimized version must sync the
    file there themselves (see PLAN.md).
    """
    module = DigestGenerator()
    if COMPILED_PROGRAM_PATH.exists():
        module.load(str(COMPILED_PROGRAM_PATH))
    return module


def generate_digest_markdown(formatted_articles: str) -> str:
    """Generate digest Markdown from already-formatted article text.

    Args:
        formatted_articles: Article text as built by `_format_articles`, or an
            equivalent caller-built numbered list (see `create_news_digest`).

    Returns:
        The generated Markdown digest.
    """
    return load_compiled_digest_generator()(articles=formatted_articles).digest
