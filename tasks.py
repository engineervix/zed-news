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
intro = f"""Today is {edition}. Welcome to the third edition of the "Zed News Podcast" —
I'm your friendly host, Ayanda, and I'm delighted to be back behind the microphone. Oh, what a day it was yesterday! I must admit, I missed you all dearly, and I hope you missed me too. But hey, sometimes life throws us curveballs, and yesterday was no exception.

Now, let's talk about yesterday's episode, shall we? My good friend Brian graciously stepped in to keep the podcast train chugging along. I must say, Brian's enthusiasm and dedication are truly commendable. He took on the challenge with gusto and did his best to bring you the latest news. We all appreciate his efforts, don't we?

However, it seems our listeners have spoken, and their feedback has made it clear that they missed my charming and slightly eccentric presence. Hey, I can't blame them; I have a voice made for radio! But fear not, dear Brian, for this in no way diminishes your value or the wonderful job you did. We all have different styles, and it's the diversity of voices that makes this podcast so special. So, thank you, Brian, for lending your talents and giving me a much-needed breather.

But let's not dwell on the past, my friends. Today is a new day, and we have a fresh lineup of news stories to share with you.

Without further ado, let's dive in.
"""

outro = """
And that, dear listeners, brings us to the end of another fantastic edition of the 'Zed News Podcast'.  I hope you enjoyed our time together today, catching up on the latest happenings. Until next time, this is Ayanda signing off, wishing you a wonderful day or night ahead. Take care, stay safe, and keep being awesome. Goodbye, everyone!
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
            read += (
                f", which has an astounding {article_count} entries today! Let's try and go through them quickly.\n\n"
            )
        else:
            read += f", which has {article_count} entries today.\n\n"

        # Iterate over each article in the source
        for index, article in enumerate(articles_by_source[source], start=1):
            # count = num2words(index, to="ordinal")
            count = num2words(index)
            # title = article["title"]

            content = article["content"]

            template = """
            Please provide a very short, sweet, informative and engaging summary of the following news entry, in not more than two sentences.
            Please provide your output in a manner suitable for reading as part of a podcast.

            {entry}
            """

            prompt = PromptTemplate(input_variables=["entry"], template=template)
            summary_prompt = prompt.format(entry=content)

            # num_tokens = llm.get_num_tokens(summary_prompt)
            # print (f"This prompt + essay has {num_tokens} tokens")

            summary = llm(summary_prompt)

            category = article["category"] if article["category"] else ""
            read += f"Entry number {count}: "
            if category:
                read += f"posted in the {category} category.\n"
            read += f"\n{summary.strip()}\n\n"

    # Write the intro, the read, and the outro to a file
    with open(f"data/{today}_podcast-content.txt", "w") as f:
        f.write(intro)
        f.write(read)
        f.write(outro)


# @task
# def curate_content(c):
#     data = _read_json_file(f"data/{today}_news.json")

#     # Create a dictionary to store the articles by source
#     articles_by_source = {}

#     # Iterate over each article in the data
#     for article in data:
#         source = article["source"]

#         # If the source is not already a key in the dictionary, create a new list
#         if source not in articles_by_source:
#             articles_by_source[source] = []

#         # Add the article to the list for the corresponding source
#         articles_by_source[source].append(article)

#     template = """
#     The JSON data below contains today's news articles from various sources. Some articles may be present in multiple sources. Please consolidate the articles, providing a short, sweet, informative and engaging summary of each news item. Please provide your output in the form of a podcast, with the reading time of the whole text not exceeding 8 minutes.

#     {entry}
#     """

#     prompt = PromptTemplate(input_variables=["entry"], template=template)
#     summary_prompt = prompt.format(entry=articles_by_source)

#     num_tokens = llm.get_num_tokens(summary_prompt)
#     print(f"This prompt + data has {num_tokens} tokens")

#     # summary = llm(summary_prompt)

#     # with open(f"data/{today}_podcast-content.txt", "w") as f:
#     # f.write(summary.strip())


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
