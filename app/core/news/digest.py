import logging
import re
import sys

from app.core.summarization.backends.together import client
from app.core.utilities import DATA_DIR, today_human_readable, today_iso_fmt

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

    # Remove any literal HTML line breaks inserted by the model
    text = remove_html_breaks(text)

    # Remove any occurrences of "Why this matters:" lines
    text = remove_why_this_matters(text)

    # Drop any Overview section if present
    text = remove_overview_section(text)

    # Remove excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Ensure consistent bullet point formatting
    text = re.sub(r"^[\*\-]\s+", "* ", text, flags=re.MULTILINE)

    return text.strip()


def normalize_section_headings(text: str) -> str:
    """Normalize headings to a canonical set used by the front-end."""
    replacements: dict[str, str] = {
        r"^#+\s*Overview.*$": "## Overview",
        # Map variants of the main stories heading to a single canonical label
        r"^#+\s*(Key Stories.*|Today'?s Top 8 Stories.*|Main Stories.*)$": "## Main Stories",
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
    """Previously enforced Title + <br> + content format; now deprecated.

    Preserve input as-is (no-op) to avoid inserting HTML tags in Markdown.
    """
    return text


def remove_html_breaks(text: str) -> str:
    """Remove literal HTML line breaks that would render as text in Markdown parser with html=False."""
    # Remove common variants of <br>
    text = re.sub(r"\s*<\s*br\s*/?\s*>\s*", "\n", text, flags=re.IGNORECASE)
    if "&lt;br" in text:
        text = text.replace("&lt;br&gt;", "\n").replace("&lt;br/&gt;", "\n")
    return text


def remove_why_this_matters(text: str) -> str:
    """Remove the leading 'Why this matters:' label if present on lines."""
    # Remove bolded or plain variants
    text = re.sub(r"^\*\*?\s*Why this matters:\s*\*\*?\s*", "", text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r"^Why this matters:\s*", "", text, flags=re.IGNORECASE | re.MULTILINE)
    return text


def remove_overview_section(text: str) -> str:
    """Remove the '## Overview' section entirely (until the next heading)."""
    pattern = r"^##\s*Overview\s*\n(?:.*?)(?=^##\s|\Z)"
    return re.sub(pattern, "", text, flags=re.MULTILINE | re.DOTALL)


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

    model = "deepseek-ai/DeepSeek-R1-0528-tput"
    temperature = 0.6
    max_tokens = 4096

    prompt = f"""
    You are a patriotic Zambian news editor creating a daily news digest in Markdown for your fellow citizens. Your tone is professional yet engaging, highlighting why the news matters to the nation.

    <sections>
    - ## Main Stories
    - ## Other Notable Stories
    - ## Key Takeaways & Watchpoints
    </sections>

    <requirements>
    - Adopt a patriotic and insightful perspective. Explain not just WHAT happened, but WHY it's significant for Zambia and its people. Use inclusive language ('our nation', 'we').
    - Where appropriate, and only for less serious topics, inject a touch of light-hearted, quintessentially Zambian humour. Keep it clever and subtle. Avoid humour on sensitive topics like crime, accidents, or political tensions.
    - Start with a single introductory paragraph (2–3 factual sentences) summarising the key themes of the day from a national perspective. No heading.
    - After the paragraph, output exactly the three sections above, in that order. No extra text before/after.
        - Main Stories: ordered list of the most significant national stories. Select stories that have the widest impact, such as national policy changes, major legal cases, economic trends, or issues directly affecting daily life for Zambians (e.g., energy, public services). Do NOT limit the number of stories.
      For each item, use exactly this layout:
      1. Title
         1–2 factual sentences with concrete details taken ONLY from the input, framed to highlight its relevance to Zambians.
    - Do NOT include “Why this matters:” or any similar editorial labels; the relevance should be woven into the summary itself.
    - Other Notable Stories: group by bold category labels (e.g., **Governance & Justice:**) with * bullets. Only include items where at least one concrete detail (name, number, date, place) is present in the input.
    - Key Takeaways & Watchpoints: 2–3 concise, forward-looking watchpoints that are fact-based (no speculation) and relevant to national interests.
    - No markdown links or HTML. Plain text only.
    - Exclude any item that has only a headline with no supporting details in the input.
    - Maintain a factual basis. Do not infer beyond the provided input, but frame the facts to be relevant to a Zambian audience.
    </requirements>

    <input>
    {digest_content}
    </input>
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
        top_p=0.95,
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
