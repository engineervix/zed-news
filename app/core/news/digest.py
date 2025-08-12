import datetime
import logging
import re
import sys
from typing import Callable

from app.core.db.models import Article
from app.core.summarization.backends.together import brief_summary, client
from app.core.utilities import DATA_DIR, today, today_human_readable, today_iso_fmt

logger = logging.getLogger(__name__)


def remove_think_tags(text: str) -> str:
    """Remove <think> tags and their content from DeepSeek-R1 responses"""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)


def fix_markdown_headings(text: str) -> str:
    """Fix markdown headings that might be missing spaces after hash characters"""
    return re.sub(r"^(#{1,6})([^\s#])", r"\1 \2", text, flags=re.MULTILINE)


def remove_title_headings(text: str) -> str:
    """Remove title-level headings (single # at start of line) from text"""
    return re.sub(r"^# .*\n?", "", text, flags=re.MULTILINE)


def clean_digest_output(text: str) -> str:
    """Clean and standardize the digest output"""
    # Remove think tags
    text = remove_think_tags(text)

    # Remove title-level headings
    text = remove_title_headings(text)

    # Fix markdown headings
    text = fix_markdown_headings(text)

    # Strip markdown-style links to keep titles/content plain: [Title](url) -> Title
    text = strip_markdown_links(text)

    # Normalize section headings to canonical set
    text = normalize_section_headings(text)

    # Ensure key story items use Title + <br> + content format
    text = standardize_key_story_title_breaks(text)

    # Remove excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Ensure consistent bullet point formatting
    text = re.sub(r"^[\*\-]\s+", "* ", text, flags=re.MULTILINE)

    return text.strip()


def normalize_section_headings(text: str) -> str:
    """Normalize headings to a canonical set used by the front-end."""
    replacements: dict[str, str] = {
        r"^#+\s*Overview.*$": "## Overview",
        r"^#+\s*(Key Stories.*|Today'?s Top 8 Stories.*)$": "## Today’s Top 8 Stories",
        r"^#+\s*(Other Notable.*)$": "## Other Notable Stories",
        r"^#+\s*(Key Takeaways.*|Takeaways.*|Watch.*)$": "## Key Takeaways & Watchpoints",
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE | re.MULTILINE)
    return text


def strip_markdown_links(text: str) -> str:
    """Convert [text](url) or [text](#) to plain text."""
    return re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)


def standardize_key_story_title_breaks(text: str) -> str:
    """Ensure each ordered key story uses Title + <br> + content format.

    Handles cases like "1. **[Title]** rest" or "1. **Title** rest".
    """

    def repl(match: re.Match) -> str:
        title = match.group(1).strip()
        rest = match.group(2).strip()
        return f"{title}\n<br>\n{rest}"

    # Convert bolded titles to Title + <br> + rest
    text = re.sub(r"^\d+\.\s*\*\*\[?(.+?)\]?\*\*\s+(.+)$", repl, text, flags=re.MULTILINE)

    return text


def update_article_with_summary(title: str, url: str, date: datetime.date, summary: str):
    """Find an article by title, URL & date, and update it with the given summary"""
    article = Article.select().where((Article.title == title) & (Article.url == url) & (Article.date == date)).first()
    if article:
        article.summary = summary
        article.save()
    else:
        logger.warning(f"Could not find article with title '{title}', URL '{url}', and date '{date}'")


def create_news_digest(news: list[dict[str, str]], dest: str, summarizer: Callable):
    """Create a news digest from the news articles using the provided summarization function"""

    articles_by_source: dict[str, list[dict[str, str]]] = {}

    for article in news:
        source = article["source"].replace("Zambia National Broadcasting Corporation (ZNBC)", "ZNBC")

        if source not in articles_by_source:
            articles_by_source[source] = []

        articles_by_source[source].append(article)

    # Create structured content for the digest
    digest_content = ""
    counter = 0
    article_summaries = []

    for source in articles_by_source:
        for article in articles_by_source[source]:
            title = article["title"]
            text = article["content"]

            if len(news) < 36:
                summary = summarizer(text, title)
            else:
                summary = brief_summary(text, title)

            if summary.strip().startswith("Summary: "):
                summary = summary.replace("Summary: ", "")

            update_article_with_summary(title, article["url"], today, summary)

            counter += 1

            article_summaries.append(
                {
                    "id": counter,
                    "title": title,
                    "source": source,
                    "url": article["url"],
                    "summary": summary.strip(),
                    "category": article.get("category"),
                }
            )

            digest_content += f"{counter}. {title} (source: {source})\n"
            digest_content += f"{summary.strip()}\n\n"

    # Write the raw content to a file for reference
    metadata = f"Title: Zed News Digest\nDate: {today_human_readable}\n\n"
    with open(f"{DATA_DIR}/{today_iso_fmt}_news_headlines.txt", "w") as f:
        f.write(metadata + "News Items:\n\n" + digest_content)

    model = "deepseek-ai/DeepSeek-R1-0528-tput"
    temperature = 0.35
    max_tokens = 4096

    prompt = f"""
You are generating Markdown content for a daily news digest on {today_human_readable}.

Rules:
- Do NOT include a page title anywhere in the body. The page title is handled by the site.
- Use ONLY these section headings, in this order:
  ## Overview
  ## Today’s Top 8 Stories
  ## Other Notable Stories
  ## Key Takeaways & Watchpoints
- Under “Today’s Top 8 Stories” produce EXACTLY 8 ordered list items (1–8).
  Each item MUST follow this exact format:
  1. Title
     <br>
     **Why this matters:** one bold sentence. Then 1–2 sentences of context with a concrete detail.
- Under “Other Notable Stories”, group items by bold category labels (e.g., **Governance & Justice:**) and use * bullets for items.
- Under “Key Takeaways & Watchpoints”, produce 2–3 concise bullet points.
- No markdown links or HTML tags other than a single <br> after each story title.
- Neutral, analytical tone. Avoid repetition. Use specific names, numbers, and dates found in the input only.
- Do not output content before or after these four sections.

TODAY'S NEWS ITEMS:

{digest_content}
"""

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    logger.info(completion)

    generated_digest = completion.choices[0].message.content

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
