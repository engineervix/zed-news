import datetime
import logging
import random

import cohere
from langchain import OpenAI, PromptTemplate
from num2words import num2words
from pydantic import HttpUrl

from app.core.db.models import Article, Episode
from app.core.utilities import COHERE_API_KEY, OPENAI_API_KEY, podcast_host, today, today_human_readable

llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
co = cohere.Client(COHERE_API_KEY)


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


async def random_opening():
    episode_number = num2words(await get_episode_number(), to="ordinal")
    data = [
        f"Today is {today_human_readable}. Welcome to the {episode_number} edition of the Zed News Podcast — I'm your friendly host, {podcast_host}, and I'm thrilled to have you join me on this journey of exploring the latest news and stories from across Zambia.",
        f"Today is {today_human_readable}. Welcome to the {episode_number} installment of the Zed News Podcast! I'm your host, {podcast_host}, and I'm excited to have you accompany me as we embark on a voyage through the latest news and stories from across Zambia.",
        f"Greetings and a warm welcome to the {episode_number} edition of the Zed News Podcast! It's {today_human_readable}, and I'm your host, {podcast_host}. Join me as we dive into the dynamic world of news and uncover the intriguing narratives shaping Zambia's landscape.",
        f"It's {today_human_readable}. I am thrilled to have you here for the {episode_number} edition of the Zed News Podcast! This is your host, {podcast_host}. Together, let's embark on an enriching journey through the vibrant tapestry of news and stories that define Zambia.",
        f"Welcome! It's a pleasure to have you join me today for the {episode_number} installment of the Zed News Podcast! I'm {podcast_host}, your friendly guide through the ever-evolving news landscape of Zambia. Get ready to immerse yourself in the latest headlines and captivating narratives that await us.",
        f"Here we are, on {today_human_readable}, marking the {episode_number} edition of the Zed News Podcast! I'm {podcast_host}, your enthusiastic host, and I'm delighted to have you with me as we traverse the vast expanse of news and stories that illuminate the heart of Zambia.",
    ]

    return random.choice(data)


def random_intro():
    data = [
        "Whether you're commuting, relaxing at home, or going about your day, the Zed News Podcast is designed to keep you informed and engaged. We know your time is valuable, so we'll deliver the news in a concise yet captivating format, allowing you to stay updated without feeling overwhelmed.",
        "In today's episode, we'll dive into the headlines making waves across Zambia. Sit back, relax, and let's explore the stories that shape our nation.",
        "As we delve into the news landscape, we'll bring you a curated selection of the most important stories from various sources. Stay tuned for a brief overview of what's happening in Zambia.",
        "Join me on this informative journey as we uncover the latest developments and provide you with a snapshot of the events happening around Zambia and beyond.",
        "Our automated curation process scours the web to compile the most relevant news stories just for you. Get ready for a concise yet comprehensive rundown of the news buzzing in Zambia.",
        "With our advanced algorithms, we've handpicked the top stories that matter. From breaking news to compelling features, we'll keep you up to date with the pulse of Zambia.",
    ]

    return random.choice(data)


def random_dig_in():
    variations = [
        "Without any more delay, let's jump right in.",
        "No time to waste, let's get started.",
        "Let's not wait any longer, it's time to delve in.",
        "Without further ado, let's dive in.",
        "Without prolonging the anticipation, let's begin our exploration.",
        "Time to embark on our news journey. Let's get to it.",
    ]

    return random.choice(variations)


def random_outro():
    variations = [
        f"And that, dear listeners, brings us to the end of another fantastic edition of the 'Zed News Podcast'. I hope you enjoyed our time together today, catching up on the latest happenings. Until next time, this is {podcast_host} signing off, wishing you a wonderful day or night ahead. Take care, stay safe, and keep being awesome. Later!",
        f"And with that, we come to the conclusion of another captivating edition of the 'Zed News Podcast'. I hope you found our exploration of the news landscape insightful and illuminating. Until we meet again, this is {podcast_host} bidding you farewell, wishing you a remarkable day or night. Stay informed, and keep making a difference. Goodbye!",
        f"That brings us to the end of this remarkable episode of the 'Zed News Podcast'. I trust you found our discussion enlightening and thought-provoking. Until next time, this is {podcast_host}, your host, signing off. Take care and see you later!",
        f"And with that, we wrap up another exciting edition of the 'Zed News Podcast'. I hope you enjoyed our time together, staying up to date with the latest news. Until we reconvene, this is {podcast_host}, your friendly voice in the news, saying farewell. Bye for now!",
        f"That concludes our journey through this edition of the 'Zed News Podcast'. I trust you found our exploration of the news landscape insightful and illuminating. Until our paths cross again, this is {podcast_host}, your guide in the realm of information, bidding you adieu. Bye bye for now!",
        f"And so, we reach the end of another remarkable episode of the 'Zed News Podcast'. I hope you found our curation and storytelling captivating and informative. Until we meet again, this is {podcast_host}, your companion on the news adventure, signing off. May your day or night be filled with meaningful connections, profound discoveries, and a commitment to positive change. God willing, see you in the next episode!",
        f"That brings us to the conclusion of this edition of the 'Zed News Podcast'. I hope you enjoyed our exploration of the news landscape and gained valuable insights. Until our paths cross again, this is {podcast_host}, your friendly host, bidding you farewell. Goodbye folks!",
    ]
    return random.choice(variations)


many_articles_adjectives = [
    "an astounding",
    "a remarkable",
    "an incredible",
    "a massive",
    "a staggering",
]
dive_in_choices = [
    "explore the stories",
    "delve into the content",
    "dig into them",
    "uncover what's inside",
    "take a quick look at each one",
    "get immersed in the news",
    "check them out",
    "navigate through them",
    "journey through the stories",
    "examine the details",
]


async def create_transcript(news: list[dict[str, str]], dest: str):
    """Create a podcast transcript from the news, and write it to a file

    Args:
        news (list[dict[str, str]]): A list of news articles represented as
            dictionaries, where each dictionary contains the following keys:
            - 'source': The article source.
            - 'url': The URL of the article.
            - 'title': The title of the article.
            - 'content': The content of the article. This is passed to the OpenAI API for summarization.
            - 'category': The category of the article.
        dest (str): The destination file path where the transcript will be written.

    Raises:
        - OpenAIException: If there is an issue with the OpenAI API.
        - TimeoutError: If the summarization request times out.
        - ConnectionError: If there is a network connectivity issue.
        - ValueError: If the input data is invalid or in the wrong format.
        - TypeError: If the input data is of incorrect type.

    Returns:
        None: The function writes the transcript to the specified file but does not return any value.
    """

    # Create a dictionary to store the articles by source
    articles_by_source = {}

    # Iterate over each article in the news list
    for article in news:
        source = article["source"].replace("Zambia National Broadcasting Corporation (ZNBC)", "ZNBC")

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
            read += f", which has {random.choice(many_articles_adjectives)} {article_count} entries today! Let's {random.choice(dive_in_choices)}.\n\n"
        else:
            read += f", which has {article_count} entries today.\n\n"

        # Iterate over each article in the source
        for index, article in enumerate(articles_by_source[source], start=1):
            count = num2words(index)
            count_ordinal = num2words(index, to="ordinal")
            count_variations = [
                f"Entry number {count} ",
                f"The {count_ordinal} entry ",
            ]

            title = article["title"]

            content = article["content"]

            # =============== Summarize using OpenAI ===============
            template = """
            Please provide a very short, sweet, informative and engaging summary of the following news entry, in not more than two sentences.
            Please provide your output in a manner suitable for reading as part of a podcast.

            {entry}
            """

            prompt = PromptTemplate(input_variables=["entry"], template=template)
            summary_prompt = prompt.format(entry=content)

            num_tokens = llm.get_num_tokens(summary_prompt)
            logging.info(f"'{title}' and its prompt has {num_tokens} tokens")

            summary = llm(summary_prompt)

            # =============== Summarize using Cohere ===============
            # logging.info(f"Summarizing '{title}' via Cohere ...")
            # # https://docs.cohere.com/reference/summarize-2
            # response = co.summarize(
            #     text=content,
            #     model="summarize-xlarge",
            #     temperature=0,
            #     length="auto",
            #     format="paragraph",
            #     extractiveness="auto",
            #     additional_command="in a manner suitable for reading as part of a podcast",
            # )
            # summary = response.summary

            await update_article_with_summary(title, article["url"], today, summary)

            category = article["category"] if article["category"] else ""
            read += f"{random.choice(count_variations)} is entitled '{title}' "
            if category:
                read += f"and was posted in the {category} category."
            read += f"\n{summary.strip()}\n\n"

    opener = await random_opening()
    intro = f"""{opener}

    {random_intro()}

    {random_dig_in()}
    """

    # Write the intro, the read, and the outro to a file
    with open(dest, "w") as f:
        f.write(intro)
        f.write(read)
        f.write(random_outro())
