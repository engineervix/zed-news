import datetime
import logging
import sys
from typing import Callable

import together
from pydantic import HttpUrl

from app.core.db.models import Article, Episode
from app.core.summarization.backends.together import brief_summary
from app.core.utilities import DATA_DIR, TOGETHER_API_KEY, podcast_host, today, today_human_readable, today_iso_fmt


async def get_episode_number() -> int:
    """Returns the episode number based on the number of episodes in the database"""
    count = await Episode.filter(live=True).count()
    return count + 1


async def update_article_with_summary(title: str, url: HttpUrl, date: datetime.date, summary: str):
    """Find an article by title, URL & date, and update it with the given summary"""
    article = await Article.filter(title=title, url=url, date=date).first()
    if article:
        article.summary = summary
        await article.save()
    else:
        logging.warning(f"Could not find article with title '{title}', URL '{url}', and date '{date}'")


async def create_transcript(news: list[dict[str, str]], dest: str, summarizer: Callable):
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

        prompt = f"You are {podcast_host}, an accomplished, fun and witty scriptwriter, content creator and podcast host. You have a news and current affairs podcast which runs Monday to Friday. Your assistant has gathered the news from various sources as indicated below. Study the content, consolidate any similar news items from different sources, and organize the news in a logical, coherent manner so it's easy to follow. You can then go ahead and present today's episode, ensuring that you cover all the news from all the sources, as curated by your assistant. At the end, add a fun and witty remark informing your audience that you are actually an AI, and not a human. Remember: leave no news item behind.\n\n"

    metadata = f"Title: Zed News Podcast episode {await get_episode_number()}\nDate: {today_human_readable}\nHost: {podcast_host}\n\n"

    content = ""
    counter = 0
    for source in articles_by_source:
        # Iterate over each article in the source
        for article in articles_by_source[source]:
            title = article["title"]
            text = article["content"]

            if len(news) < 15:
                # If there are less than 15 articles, summarize each article in the usual way
                summary = summarizer(text, title)
            else:
                summary = brief_summary(text, title)

            await update_article_with_summary(title, article["url"], today, summary)

            counter += 1

            content += f"{counter}. '{title}' (source: {source})"
            content += f"\n{summary.strip()}\n\n"

    notes = prompt + "```\n" + metadata + "News Items:\n\n" + content + "```"

    # Write the content to a file
    with open(f"{DATA_DIR}/{today_iso_fmt}_news_headlines.txt", "w") as f:
        f.write(metadata + "News Items:\n\n" + content)

    model = "lmsys/vicuna-13b-v1.5-16k"
    temperature = 0.7
    max_tokens = 6144
    together.api_key = TOGETHER_API_KEY
    output = together.Complete.create(
        prompt=notes,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    logging.info(output)

    transcript = output["output"]["choices"][0]["text"]

    if transcript:
        # Write the transcript to a file
        with open(dest, "w") as f:
            f.write(transcript)
    else:
        logging.error("Transcript is empty")
        sys.exit(1)
