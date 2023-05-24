import os
import datetime
import json
import glob

import pytz
import requests
from invoke import task
from num2words import num2words
from dotenv import load_dotenv
from langchain import OpenAI
from langchain import PromptTemplate

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
XI_API_KEY = os.getenv("XI_API_KEY")
llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)


def suffix(d):
    return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")


def custom_strftime(format, t):
    return t.strftime(format).replace("{S}", str(t.day) + suffix(t.day))


timezone = pytz.timezone("Africa/Lusaka")
today = datetime.datetime.now(timezone).date().isoformat()
edition = custom_strftime("%A {S} %B, %Y", datetime.datetime.now(timezone).date())
intro = f"""Today is {edition}. Welcome to the second edition of the "Zed News Podcast" —
I'm your friendly host, Brian, an AI standing in for my colleague Ayanda, who hosted the first edition of the podcast yesterday.
As usual, we've gathered the latest updates from various sources, saving you time and keeping you informed about all that's happening in the country.

Without further ado, let's dive in.
"""

outro = f"""
Ladies and gentlemen, that's it for today!

Thank you for joining us on the second edition of 'Zed News Podcast.' We hope you enjoyed our auto-curated selection of news stories from across the country. Until the next time, goodbye!
"""


@task
def fetch_znbc_news(c):
    c.run("python src/fetch_znbc_news.py", pty=True)


@task
def fetch_other_news(c):
    c.run("python src/fetch_other_news.py", pty=True)


@task
def combine_json_files(c):
    """Combine JSON files"""

    json_files = glob.glob("data/_*.json")
    data = []
    for json_file in json_files:
        with open(json_file) as f:
            data.extend(json.load(f))

    with open(f"data/{today}_news.json", "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _read_json_file(file):
    with open(file) as f:
        return json.load(f)


@task
def create_podcast_content(c):
    """Create content for the podcast

    Steps:
    0. read data from data/{today}_news.json
    1. categorize the data by source
    2. write a brief intro welcoming the listener to the podcast
    3. for each source:
        - mention that we're reading from the source
        - for each news item:
            - read the title
            - if item has category, specify that it was posted in that category
            - read the content
    4. write a brief outro thanking the listener for listening to the podcast
    """

    data = _read_json_file(f"data/{today}_news.json")

    # Create a dictionary to store the articles by source
    articles_by_source = {}

    # Iterate over each article in the data
    for article in data:
        source = article["source"]

        # If the source is not already a key in the dictionary, create a new list
        if source not in articles_by_source:
            articles_by_source[source] = []

        # Add the article to the list for the corresponding source
        articles_by_source[source].append(article)

    read = ""

    for count, source in enumerate(articles_by_source, start=1):
        if count == 1:
            read += "We are going to start with news from "
        elif count == len(articles_by_source):
            read += "To wrap up today's edition, let's check out the news from "
        else:
            read += "Next up, we have news from "

        read += source

        article_count = len(articles_by_source[source])
        if article_count > 9:
            read += f", which has an astounding {article_count} entries today! Let's go through them quickly.\n\n"
        else:
            read += f", which has {article_count} entries today.\n\n"

        # Iterate over each article in the source
        for index, article in enumerate(articles_by_source[source], start=1):
            count = num2words(index, to="ordinal")
            title = article["title"]

            content = article["content"]

            template = """
            Please provide a concise summary of the following news entry.
            Please make it short and sweet, but also informative and engaging.
            It should be no more than three sentences long.
            Please provide your output in a manner suitable for reading as part of a podcast.

            {entry}
            """

            prompt = PromptTemplate(input_variables=["entry"], template=template)
            summary_prompt = prompt.format(entry=content)

            # num_tokens = llm.get_num_tokens(summary_prompt)
            # print (f"This prompt + essay has {num_tokens} tokens")

            summary = llm(summary_prompt)

            category = article["category"] if article["category"] else ""
            read += f"The {count} entry is entitled '{title}' "
            if category:
                read += f"and was posted in the {category} category."
            read += f"\n{summary.strip()}\n\n"

    # Write the intro, the read, and the outro to a file
    with open(f"data/{today}_podcast-content.txt", "w") as f:
        f.write(intro)
        f.write(read)
        f.write(outro)


@task
def create_audio(c):
    """Create audio from the podcast content"""

    # https://api.elevenlabs.io/v1/voices
    voice_id = "EXAVITQu4vr4xnSDxMaL"  # Bella

    CHUNK_SIZE = 1024
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": XI_API_KEY}

    with open(f"data/{today}/{today}_podcast-content.txt") as f:
        content = f.read()

    data = {
        "text": content,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }

    response = requests.post(url, json=data, headers=headers)
    with open(f"data/zed_news_{today}.mp3", "wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
