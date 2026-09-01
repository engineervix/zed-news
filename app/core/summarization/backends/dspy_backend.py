from dataclasses import dataclass

import dspy


@dataclass
class Digest:
    content: str
    total_articles: int
    sources: list[str]


class DigestSignature(dspy.Signature):
    """Write a Zambian news digest in Markdown from the given articles."""

    articles: str = dspy.InputField(desc="Numbered list of articles with title, source, and content")
    digest: str = dspy.OutputField(
        desc="Markdown digest with Main Stories, Other Notable Stories, and Key Takeaways & Watchpoints sections"
    )


class DigestGenerator(dspy.Module):
    def __init__(self):
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
