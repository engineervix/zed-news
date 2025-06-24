import datetime
import logging
import re
import sys
from typing import Callable

from openai import OpenAI
from pydantic import HttpUrl

from app.core.db.models import Article
from app.core.summarization.backends.together import brief_summary
from app.core.utilities import DATA_DIR, today, today_human_readable, today_iso_fmt

logger = logging.getLogger(__name__)


def fix_markdown_headings(text: str) -> str:
    """Fix markdown headings that might be missing spaces after hash characters

    Args:
        text: The text content to fix

    Returns:
        Text with properly formatted markdown headings

    Examples:
        >>> fix_markdown_headings("##Main Stories\\n###Subsection")
        "## Main Stories\\n### Subsection"
    """
    return re.sub(r"^(#{1,6})([^\s#])", r"\1 \2", text, flags=re.MULTILINE)


def remove_title_headings(text: str) -> str:
    """Remove title-level headings (single # at start of line) from text

    Args:
        text: The text content to process

    Returns:
        Text with title-level heading lines removed

    Examples:
        >>> remove_title_headings("# Title\\n## Section\\nContent")
        "## Section\\nContent"
        >>> remove_title_headings("# Title without newline")
        ""
    """
    return re.sub(r"^# .*\n?", "", text, flags=re.MULTILINE)


def update_article_with_summary(title: str, url: HttpUrl, date: datetime.date, summary: str):
    """Find an article by title, URL & date, and update it with the given summary"""
    article = Article.select().where((Article.title == title) & (Article.url == url) & (Article.date == date)).first()
    if article:
        article.summary = summary
        article.save()
    else:
        logger.warning(f"Could not find article with title '{title}', URL '{url}', and date '{date}'")


def create_news_digest(news: list[dict[str, str]], dest: str, summarizer: Callable):
    """Create a news digest from the news articles using the provided summarization function
    and write it to a file

    Args:
        news (list[dict[str, str]]): A list of news articles represented as
            dictionaries, where each dictionary contains the following keys:
            - 'source': The article source.
            - 'url': The URL of the article.
            - 'title': The title of the article.
            - 'content': The content of the article. This is passed to the OpenAI API for summarization.
            - 'category': The category of the article.
        dest (str): The destination file path where the digest will be written.
        summarizer (Callable): The function to use for summarization. This function must accept two arguments:
            - content (str): The content of the article.
            - title (str): The title of the article.

    Raises:
        - OpenAIException: If there is an issue with the OpenAI API.
        - TimeoutError: If the summarization request times out.
        - ConnectionError: If there is a network connectivity issue.
        - ValueError: If the input data is invalid or in the wrong format.
        - TypeError: If the input data is of incorrect type.

    Returns:
        None: The function writes the digest to the specified file but does not return any value.
    """

    articles_by_source = {}

    for article in news:
        source = article["source"].replace("Zambia National Broadcasting Corporation (ZNBC)", "ZNBC")

        # If the source is not already a key in the dictionary, create a new list
        if source not in articles_by_source:
            articles_by_source[source] = []

        # Add the article to the list for the corresponding source
        articles_by_source[source].append(article)

    # Create structured content for the digest
    digest_content = ""
    counter = 0
    article_summaries = []

    for source in articles_by_source:
        # Iterate over each article in the source
        for article in articles_by_source[source]:
            title = article["title"]
            text = article["content"]

            if len(news) < 36:
                # If there are less than 36 articles, summarize each article in the usual way
                summary = summarizer(text, title)
            else:
                summary = brief_summary(text, title)

            if summary.strip().startswith("Summary: "):
                summary = summary.replace("Summary: ", "")

            update_article_with_summary(title, article["url"], today, summary)

            counter += 1

            # Store article data for digest generation
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

            digest_content += f"{counter}. '{title}' (source: {source})"
            digest_content += f"\n{summary.strip()}\n\n"

    # Write the raw content to a file for reference
    metadata = f"Title: Zed News Digest\nDate: {today_human_readable}\n\n"
    with open(f"{DATA_DIR}/{today_iso_fmt}_news_headlines.txt", "w") as f:
        f.write(metadata + "News Items:\n\n" + digest_content)

    # Generate a cohesive news digest using OpenAI
    model = "gpt-4.1-nano"
    temperature = 0.7
    max_tokens = 3096

    client = OpenAI()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a skilled news editor creating a daily digest of Zambian news for a Zambian audience. "
                    "Your goal is to create a clear, well-organized synthesis that readers can quickly scan and understand.\n\n"
                    "ANALYSIS PHASE:\n"
                    "Before writing, analyze the news items to:\n"
                    "1. Group stories into logical themes (Economy, Environment, Technology, Agriculture, Politics, Safety/Crime, Sports, etc.)\n"
                    "2. Identify the 3-5 most significant stories that deserve prominence\n"
                    "3. Note connections and patterns between stories\n"
                    "4. Determine which stories provide broader context about Zambia's current situation\n\n"
                    "STRUCTURE REQUIREMENTS:\n"
                    "Format your digest with these exact sections (DO NOT include a title - it will be added separately):\n\n"
                    "Start with an opening summary paragraph (no heading).\n\n"
                    "## Main Stories\n"
                    "- Present 5-8 key stories in order of importance\n"
                    "- Use **bold formatting** for story headlines\n"
                    "- Provide 2-3 sentences of context and analysis per story\n"
                    "- Group related stories together naturally\n"
                    "- Focus on impact and significance, not just facts\n\n"
                    "## Brief Updates\n"
                    "- Cover remaining stories in 1-2 sentences each\n"
                    "- Group by theme where possible\n\n"
                    "## Closing Reflection\n"
                    "- 2-3 sentences summarizing key takeaways\n"
                    "- What should readers remember or watch for?\n\n"
                    "TONE AND STYLE:\n"
                    "- Professional yet accessible\n"
                    "- Factual and balanced\n"
                    "- Use active voice and clear, concise language\n"
                    "- Avoid jargon; explain complex issues simply\n"
                    "- Include relevant context for international readers\n"
                    "- Maintain objectivity while highlighting significance\n\n"
                    "CRITICAL REQUIREMENTS:\n"
                    "- Incorporate ALL provided news items without repetition\n"
                    "- Use consistent formatting throughout\n"
                    "- Ensure smooth transitions between topics\n"
                    "- Prioritize stories that affect ordinary Zambians\n"
                    "- When covering politics, focus on policy impacts rather than personalities"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Create today's news digest for {today_human_readable}.\n\n"
                    "INSTRUCTIONS:\n"
                    "1. Start with a brief overview paragraph highlighting the day's main themes\n"
                    "2. Present the most important 5-8 stories with clear headlines and context\n"
                    "3. Cover remaining stories briefly, grouped by theme\n"
                    "4. End with key takeaways and what readers should watch for\n"
                    "5. Use clear formatting with numbered lists or bullet points for easy scanning\n"
                    "6. Ensure ALL news items below are incorporated\n\n"
                    "**Today's News Items:**\n\n" + f"{digest_content}"
                ),
            },
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    logger.info(completion)

    generated_digest = completion.choices[0].message.content

    if generated_digest := generated_digest.strip():
        # Remove title-level headings since title is added separately
        generated_digest = remove_title_headings(generated_digest)

        # Fix markdown headings that might be missing spaces
        generated_digest = fix_markdown_headings(generated_digest)

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
