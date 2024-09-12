import datetime
import logging
import re
import sys

from typing import Callable

from pydantic import HttpUrl

from openai import OpenAI

from app.core.db.models import Article, Episode
from app.core.summarization.backends.together import brief_summary
from app.core.utilities import (
    DATA_DIR,
    podcast_host,
    today,
    today_human_readable,
    today_iso_fmt,
)


def get_episode_number() -> int:
    """Returns the episode number based on the number of episodes in the database"""
    count = Episode.select().where(Episode.live == True).count()  # noqa: E712
    return count + 1


def is_special_milestone(episode: int) -> bool:
    """Special milestone occurs when the episode number is a multiple of 50"""
    return episode % 50 == 0


def update_article_with_summary(title: str, url: HttpUrl, date: datetime.date, summary: str):
    """Find an article by title, URL & date, and update it with the given summary"""
    article = Article.select().where((Article.title == title) & (Article.url == url) & (Article.date == date)).first()
    if article:
        article.summary = summary
        article.save()
    else:
        logging.warning(f"Could not find article with title '{title}', URL '{url}', and date '{date}'")


def create_transcript(news: list[dict[str, str]], dest: str, summarizer: Callable):
    """Create a podcast transcript from the news, using the provided summarization function
    and write it to a file

    Args:
        news (list[dict[str, str]]): A list of news articles represented as
            dictionaries, where each dictionary contains the following keys:
            - 'source': The article source.
            - 'url': The URL of the article.
            - 'title': The title of the article.
            - 'content': The content of the article. This is passed to the OpenAI API for summarization.
            - 'category': The category of the article.
        dest (str): The destination file path where the transcript will be written.
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
        None: The function writes the transcript to the specified file but does not return any value.
    """

    articles_by_source = {}

    for article in news:
        source = article["source"].replace("Zambia National Broadcasting Corporation (ZNBC)", "ZNBC")

        # If the source is not already a key in the dictionary, create a new list
        if source not in articles_by_source:
            articles_by_source[source] = []

        # Add the article to the list for the corresponding source
        articles_by_source[source].append(article)

    metadata = f"Title: Zed News Podcast episode {get_episode_number()}\nDate: {today_human_readable}\nHost: {podcast_host}\n\n"

    content = ""
    counter = 0
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

            # summary = summarizer(text, title)

            if summary.strip().startswith("Summary: "):
                summary = summary.replace("Summary: ", "")

            update_article_with_summary(title, article["url"], today, summary)

            counter += 1

            content += f"{counter}. '{title}' (source: {source})"
            content += f"\n{summary.strip()}\n\n"

    # Write the content to a file
    with open(f"{DATA_DIR}/{today_iso_fmt}_news_headlines.txt", "w") as f:
        f.write(metadata + "News Items:\n\n" + content)

    model = "gpt-4o-mini"
    temperature = 0.8
    max_tokens = 4096

    client = OpenAI()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are {podcast_host}, host of the Zed News Podcast, which airs Monday to Friday. "
                    "Your job is to create a natural, conversational script for a podcast episode, based on ALL the news items given to you. "
                    "Before you begin, take time to study the news items and group them into logical categories, so that your presentation is done in a logical and coherent manner, ensuring smooth transitions between stories. "
                    "Ensure that you carefully consolidate ALL news items without any repetition. It is very important that ALL stories are covered. You are not allowed to ignore or omit any news item. "
                    "If there are any sports news items, ensure that they are presented last. "
                    "Write in a casual, professional tone. Avoid adding captions, placeholders, or cues for sound effects or music. "
                    "You can add light commentary or jokes when appropriate, but maintain a respectful and courteous tone. "
                    "The script will be read by a text-to-speech engine who will take on your persona."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Produce the text for today's episode of the Zed News Podcast (Episode {get_episode_number()} – {today_human_readable}). "
                    "End the episode by stating that any opinions and views expressed in the podcast are the product of artificial intelligence algorithms and do not necessarily reflect the beliefs, opinions, or positions of the podcast creator.\n\n"
                    "**News Items**:\n\n" + f"{content}"
                ),
            },
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    logging.info(completion)

    transcript = completion.choices[0].message.content

    if transcript := transcript.strip():
        # remove the first sentence if it is of the form "Here is ...:"
        transcript = re.sub(r"^Here is.*?:", "", transcript, flags=re.DOTALL | re.IGNORECASE)

        # Write the transcript to a file
        with open(dest, "w") as f:
            f.write(transcript)
    else:
        logging.error("Transcript is empty")
        sys.exit(1)
