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
    """Remove <think> tags and their content from DeepSeek-R1 responses

    Args:
        text: The text content to process

    Returns:
        Text with think tags and their content removed

    Examples:
        >>> remove_think_tags("<think>Reasoning here</think>Answer")
        "Answer"
        >>> remove_think_tags("Normal text without think tags")
        "Normal text without think tags"
    """
    # Remove <think> tags and everything between them
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)


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
            - 'content': The content of the article. This is passed to the OpenAI API
              for summarization.
            - 'category': The category of the article.
        dest (str): The destination file path where the digest will be written.
        summarizer (Callable): The function to use for summarization. This function
            must accept two arguments:
            - content (str): The content of the article.
            - title (str): The title of the article.

    Raises:
        - OpenAIException: If there is an issue with the OpenAI API.
        - TimeoutError: If the summarization request times out.
        - ConnectionError: If there is a network connectivity issue.
        - ValueError: If the input data is invalid or in the wrong format.
        - TypeError: If the input data is of incorrect type.

    Returns:
        None: The function writes the digest to the specified file but does not
        return any value.
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
                # If there are less than 36 articles, summarize each article in the
                # usual way
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

    # Generate a cohesive news digest using Together AI
    model = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    temperature = 0.7
    max_tokens = 3096

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Create a daily news digest for {today_human_readable} from the following Zambian news articles. "
                    "Analyze the stories to identify main themes and the most significant developments. "
                    "Group related stories and prioritize those that affect ordinary Zambians.\n\n"
                    "Structure the digest as follows:\n"
                    "1. Start with a brief overview paragraph highlighting the day's main themes\n"
                    "2. Present 5-8 key stories in order of importance using the format: 'Story Title<br>Analysis and context'\n"
                    "3. Cover remaining stories briefly in bullet points, grouped by theme\n"
                    "4. End with key takeaways and what readers should watch for\n\n"
                    "Use professional yet accessible language, focus on policy impacts rather than personalities, "
                    "and ensure all news items are incorporated without repetition.\n\n"
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
        # Remove think tags from DeepSeek-R1 reasoning
        generated_digest = remove_think_tags(generated_digest)

        # Remove title-level headings since title is added separately
        generated_digest = remove_title_headings(generated_digest)

        # Fix markdown headings that might be missing spaces
        generated_digest = fix_markdown_headings(generated_digest)

        # remove <br> tags from the generated digest
        generated_digest = generated_digest.replace("<br>", "")

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
