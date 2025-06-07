import datetime
import logging
import sys
from typing import Callable

from openai import OpenAI
from pydantic import HttpUrl

from app.core.db.models import Article
from app.core.summarization.backends.together import brief_summary
from app.core.utilities import DATA_DIR, today, today_human_readable, today_iso_fmt

logger = logging.getLogger(__name__)


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
                    "You are a skilled news editor creating a daily digest of Zambian news. "
                    "Your job is to create a clear, well-organized summary of today's news stories that readers can quickly scan and understand. "
                    "Before you begin, analyze the news items and:\n"
                    "1. Group them into logical themes or categories\n"
                    "2. Identify the most significant stories that deserve more attention\n"
                    "3. Note any connections or patterns between different stories\n"
                    "Structure your digest as follows:\n"
                    "- Start with a brief overview of the day's key themes\n"
                    "- Present stories in order of importance and relevance\n"
                    "- Group related stories together naturally\n"
                    "- Provide brief context or analysis where helpful\n"
                    "- If there are sports stories, place them at the end\n"
                    "Write in a clear, professional tone that is:\n"
                    "- Informative and factual\n"
                    "- Easy to scan and read quickly\n"
                    "- Engaging but not overly casual\n"
                    "- Respectful and balanced in presentation\n"
                    "Ensure that you incorporate ALL news items without repetition. "
                    "Focus on helping readers understand what happened and why it matters. "
                    "Do not add section headers or formatting - just write flowing, well-organized prose."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Create today's news digest for {today_human_readable}. "
                    "End with a brief reflection on the day's news and what readers should keep in mind.\n\n"
                    "**News Items**:\n\n" + f"{digest_content}"
                ),
            },
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    logger.info(completion)

    generated_digest = completion.choices[0].message.content

    if generated_digest := generated_digest.strip():
        # Clean up the generated content
        generated_digest = generated_digest.replace("**", "").replace("# ", "")

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
