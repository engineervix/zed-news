import datetime
import logging
import re
import sys

# import time
from typing import Callable

# from langchain.llms import OpenAI
from pydantic import HttpUrl

# import replicate
from together import Together

from app.core.db.models import Article, Episode
from app.core.summarization.backends.together import brief_summary
from app.core.utilities import (
    DATA_DIR,
    # OPENAI_API_KEY,
    TOGETHER_API_KEY,
    podcast_host,
    today,
    today_human_readable,
    today_iso_fmt,
)

# llm = OpenAI(temperature=0.7, openai_api_key=OPENAI_API_KEY)


def get_episode_number() -> int:
    """Returns the episode number based on the number of episodes in the database"""
    count = Episode.select().where(Episode.live == True).count()  # noqa: E712
    return count + 1


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

    if today_iso_fmt == "2024-07-01":
        prompt = f"You are {podcast_host}, a lively and funny scriptwriter, content creator, and the host of the Zed News Podcast, which runs Monday to Friday. Today is {today_human_readable}, and you're gearing up for episode number {get_episode_number()} after a five-week holiday. Your task is to present the day's news in a conversational tone, covering everything logically and coherently without repetition. Consolidate information from different sources if needed. At the end of the podcast, leave your audience with a witty anecdote to end on a high note. Remember to cover all the news items from the sources provided below, but without repeating any content. Don't worry about sound effects, music, or captions – just speak directly, naturally and engagingly as if you're live on air. Start by sharing a few highlights from your holiday and express your genuine excitement to reconnect with your loyal listeners. Thank them for their patience during your absence.\n\n"
    else:
        prompt = f"You are {podcast_host}, host of the Zed News Podcast, which runs Monday to Friday. Today is {today_human_readable}, and your task is to produce the text for episode number {get_episode_number()} based on the news items below. Your text will be read as-is by a text-to-speech engine who will take on your persona. This means that you should not add any captions or placeholders for sound effects, music, etc -- all we want is just natural, plain text. Before you begin, take time to study the news items and group them into logical categories, so that your presentation is done in a logical and coherent manner. Ensure that you consolidate all news items without any repetion whatsoever. Feel free to add constructive comments and jokes where necessary and appropriate, doing so in a courteous manner.\n\n"

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

    notes = prompt + "```\n" + content + "```"

    # Write the content to a file
    with open(f"{DATA_DIR}/{today_iso_fmt}_news_headlines.txt", "w") as f:
        f.write(metadata + "News Items:\n\n" + content)

    # model = "lmsys/vicuna-13b-v1.5-16k"
    # model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    # model = "mistralai/Mixtral-8x22B-Instruct-v0.1"
    model = "meta-llama/Llama-3-70b-chat-hf"
    # model = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    # model = "NousResearch/Nous-Hermes-2-Mixtral-8x7B-SFT"
    # model = "Qwen/Qwen1.5-14B-Chat"
    temperature = 0.8
    # top_p = 0.7
    # top_k = 60
    # repetition_penalty = 1.1
    max_tokens = 4096
    client = Together(api_key=TOGETHER_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=[{"content": notes, "role": "user"}],
        temperature=temperature,
        # top_p=top_p,
        # top_k=top_k,
        # repetition_penalty=repetition_penalty,
        max_tokens=max_tokens,
        stop=["<|eot_id|>"],
    )
    logging.info(response)

    transcript = response.choices[0].message.content

    if transcript := transcript.strip():
        # remove the first sentence if it is of the form "Here is ...:"
        transcript = re.sub(r"^Here is.*?:", "", transcript, flags=re.DOTALL | re.IGNORECASE)

        # Write the transcript to a file
        with open(dest, "w") as f:
            f.write(transcript)
    else:
        logging.error("Transcript is empty")
        sys.exit(1)

    # data = llm(notes)
    # if data:
    #     # Write the transcript to a file
    #     with open(dest, "w") as f:
    #         f.write(data)
    # else:
    #     logging.error("Transcript is empty")
    #     sys.exit(1)

    # model = replicate.models.get("meta/llama-2-70b-chat")
    # version = model.versions.get("02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3")
    # prediction = replicate.predictions.create(
    #     version=version,
    #     input={
    #         "prompt": notes,
    #         "temperature": 0.7,
    #         "max_new_tokens": 4096,
    #     },
    # )

    # # Check if the task is complete, then get the transcript
    # while True:
    #     logging.info("Checking if Replicate Task is completed...")
    #     prediction.reload()
    #     result = prediction.status
    #     if result == "succeeded":
    #         logging.info("Woohoo! Task completed!")
    #         break
    #     prediction.wait()

    # transcript = prediction.output

    # if transcript:
    #     # Write the transcript to a file
    #     with open(dest, "w") as f:
    #         f.write(transcript)
    # else:
    #     logging.error("Transcript is empty")
    #     sys.exit(1)
