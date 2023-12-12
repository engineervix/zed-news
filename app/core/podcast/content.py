import datetime
import logging
from typing import Callable

import together
from pydantic import HttpUrl

from app.core.db.models import Article, Episode
from app.core.utilities import TOGETHER_API_KEY, podcast_host, today, today_human_readable


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

    prompt = f"<human>: You are {podcast_host}, an accomplished, fun and witty scriptwriter, content creator and podcast host. You have a news and current affairs podcast which runs Monday to Friday. Your secretary has gathered the news from various sources as indicated below, so go ahead and present today's episode. Add a fun and witty remark at the end, informing your audience that you are actually an AI, and not a human.\n\n"

    metadata = f"Title: Zed News Podcast episode {await get_episode_number()}\nDate: {today_human_readable}\nHost: {podcast_host}\n\n"

    content = ""
    counter = 0
    for source in articles_by_source:
        # Iterate over each article in the source
        for article in articles_by_source[source]:
            title = article["title"]
            text = article["content"]
            summary = summarizer(text, title)

            await update_article_with_summary(title, article["url"], today, summary)

            counter += 1

            content += f"{counter}. '{title}' (source: {source})"
            content += f"\n{summary.strip()}\n\n"

    notes = prompt + "```" + metadata + "News Items:\n\n" + content + "```<bot>:"

    model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    temperature = 0.4
    top_p = 0.5
    max_tokens = 4096
    together.api_key = TOGETHER_API_KEY
    output = together.Complete.create(
        prompt=notes,
        model=model,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        repetition_penalty=1.1,
    )
    logging.info(output)

    transcript = output["output"]["choices"][0]["text"]

    # Write the content to a file
    with open(dest, "w") as f:
        f.write(transcript)
