import logging
import re
import sys

import dspy

from app.core.summarization.backends.dspy_backend import generate_digest_markdown
from app.core.utilities import DATA_DIR, TOGETHER_API_KEY, remove_think_tags, today_human_readable, today_iso_fmt

logger = logging.getLogger(__name__)

dspy.configure(
    lm=dspy.LM(
        "together_ai/deepseek-ai/DeepSeek-V4-Flash-0731",
        api_key=TOGETHER_API_KEY,
        temperature=0.6,
        max_tokens=16384,
        top_p=0.95,
        reasoning={"enabled": False},
    )
)


def fix_markdown_headings(text: str) -> str:
    """Fix markdown headings that might be missing spaces after hash characters"""
    return re.sub(r"^(#{1,6})([^\s#])", r"\1 \2", text, flags=re.MULTILINE)


def clean_digest_output(text: str) -> str:
    """Clean and standardize the digest output.

    The DSPy module (`generate_digest_markdown`) is now responsible for
    canonical section headings, no title heading, no markdown links, no
    HTML, and no "Why this matters" labels - `digest_compliance_score`
    checks all of these directly, so cleanup here would be redundant.
    What's left are defensive fixes for things the compliance metric does
    not check: reasoning leakage from the model, and cosmetic formatting.
    """
    # Remove think tags some models (e.g. DeepSeek) may leak despite reasoning being disabled
    text = remove_think_tags(text)

    # Fix markdown headings missing a space after the hash characters
    text = fix_markdown_headings(text)

    # Remove excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Ensure consistent bullet point formatting
    text = re.sub(r"^[\*\-]\s+", "* ", text, flags=re.MULTILINE)

    return text.strip()


def create_news_digest(news: list[dict[str, str]], dest: str):
    """Create a news digest from the news articles using the provided summarization function"""

    if not news:
        logger.info("No news to create digest from.")
        return

    articles_by_source: dict[str, list[dict[str, str]]] = {}

    for article in news:
        source = article["source"].replace("Zambia National Broadcasting Corporation (ZNBC)", "ZNBC")

        if source not in articles_by_source:
            articles_by_source[source] = []

        articles_by_source[source].append(article)

    # Create structured content for the digest
    # Note: Feed the model original article texts (clipped) to reduce compounding summarization
    digest_content = ""
    counter = 0
    article_summaries = []

    for source in articles_by_source:
        for article in articles_by_source[source]:
            title = article["title"]
            text = article["content"]

            # For the model input, prefer original article content to avoid layered summarization
            original_excerpt = text.strip()
            # Clip very long articles to keep prompt within token limits
            max_length = 2200
            if len(original_excerpt) > max_length:
                original_excerpt = original_excerpt[:max_length].rstrip() + "…"

            counter += 1

            article_summaries.append(
                {
                    "id": counter,
                    "title": title,
                    "source": source,
                    "url": article["url"],
                    "category": article.get("category"),
                }
            )

            digest_content += f"{counter}. {title} (source: {source})\n"
            digest_content += f"{original_excerpt}\n\n"

    # Write the raw content to a file for reference
    metadata = f"Title: Zed News Digest\nDate: {today_human_readable}\n\n"
    with open(f"{DATA_DIR}/{today_iso_fmt}_news_headlines.txt", "w") as f:
        f.write(metadata + "News Items:\n\n" + digest_content)

    generated_digest = generate_digest_markdown(digest_content)

    if generated_digest := generated_digest.strip():
        # Clean the output
        generated_digest = clean_digest_output(generated_digest)

        # Write the digest to the destination file
        with open(dest, "w") as f:
            f.write(generated_digest)

        logger.info(f"News digest created successfully: {dest}")
        return {
            "date": today_iso_fmt,
            "title": f"News Digest - {today_human_readable}",
            "content": generated_digest,
            "articles": article_summaries,
            "total_articles": len(article_summaries),
            "sources": list({article["source"] for article in article_summaries}),
        }
    else:
        logger.error("Generated digest is empty")
        sys.exit(1)
