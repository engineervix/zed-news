import datetime
import logging
import re
import sys
from typing import Callable

from pydantic import HttpUrl

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

    # Remove <br> tags
    text = text.replace("<br>", "")

    # Remove excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Ensure consistent bullet point formatting
    text = re.sub(r"^[\*\-]\s+", "* ", text, flags=re.MULTILINE)

    return text.strip()


def update_article_with_summary(title: str, url: HttpUrl, date: datetime.date, summary: str):
    """Find an article by title, URL & date, and update it with the given summary"""
    article = Article.select().where((Article.title == title) & (Article.url == url) & (Article.date == date)).first()
    if article:
        article.summary = summary
        article.save()
    else:
        logger.warning(f"Could not find article with title '{title}', URL '{url}', and date '{date}'")


def create_news_digest(news: list[dict[str, str]], dest: str, summarizer: Callable):
    """Create a news digest from the news articles using the provided summarization function"""

    articles_by_source = {}

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

            digest_content += f"{counter}. '{title}' (source: {source})\n"
            digest_content += f"{summary.strip()}\n\n"

    # Write the raw content to a file for reference
    metadata = f"Title: Zed News Digest\nDate: {today_human_readable}\n\n"
    with open(f"{DATA_DIR}/{today_iso_fmt}_news_headlines.txt", "w") as f:
        f.write(metadata + "News Items:\n\n" + digest_content)

    model = "deepseek-ai/DeepSeek-R1-0528-tput"
    temperature = 0.6
    max_tokens = 4096

    prompt = f"""<think>
I need to create a comprehensive daily news digest for {today_human_readable} from Zambian news articles. Let me analyze these stories to identify themes and prioritize by impact on ordinary Zambians.
</think>

Create a daily news digest for {today_human_readable} from the following Zambian news articles.

INSTRUCTIONS:
1. Write an overview paragraph (2-3 sentences) identifying the day's dominant themes
2. Present exactly 8 key stories in order of importance
3. Group remaining stories by theme in a brief "Other Notable Stories" section
4. End with 2-3 key takeaways and future developments to watch

FORMAT FOR KEY STORIES:
1. **[Story Title]**
[Bold statement about why this matters]. [Additional context explaining the broader implications]. [Specific detail or data point that adds depth].

GUIDELINES:
- Focus on concrete impacts on citizens, not just political drama
- Use specific numbers, dates, and names when available
- Connect stories to show patterns or contradictions
- Maintain neutral, analytical tone
- Each key story analysis should be 2-3 sentences
- Avoid repeating information between sections

TODAY'S NEWS ITEMS:

{digest_content}"""

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
