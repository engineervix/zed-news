import datetime
import logging
import random

import cohere
from langchain import OpenAI, PromptTemplate
from num2words import num2words
from pydantic import HttpUrl

from app.core.db.models import Article, Episode
from app.core.utilities import (
    COHERE_API_KEY,
    OPENAI_API_KEY,
    podcast_host,
    today,
    today_human_readable,
)

llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
co = cohere.Client(COHERE_API_KEY)


async def get_episode_number() -> int:
    """Returns the episode number based on the number of episodes in the database"""
    count = await Episode.filter(live=True).count()
    return count + 1


async def update_article_with_summary(title: str, url: HttpUrl, date: datetime.date, summary: str):
    """Find an article by title, URL & date, and update it with the given summary"""
    article = await Article.get(title=title, url=url, date=date)
    article.summary = summary
    await article.save()


async def random_opening():
    episode_number = num2words(await get_episode_number(), to="ordinal")
    data = [
        f"Today is {today_human_readable}. Welcome to the {episode_number} edition of the Zed News Podcast — I'm your friendly host, {podcast_host}, and I'm thrilled to have you join us on this journey of exploring the latest news and stories from across Zambia.",
        f"Today is {today_human_readable}. Welcome to the {episode_number} installment of the Zed News Podcast! I'm {podcast_host}, your amiable host, and I'm excited to have you accompany us as we embark on a voyage through the latest news and stories from across Zambia.",
        f"Greetings and a warm welcome to the {episode_number} edition of the Zed News Podcast! It's {today_human_readable}, and I'm your genial host, {podcast_host}. Join us as we dive into the dynamic world of news and uncover the intriguing narratives shaping Zambia's landscape.",
        f"We're thrilled to have you here on this {today_human_readable}, for the {episode_number} edition of the Zed News Podcast! I'm {podcast_host}, your affable host, and together, let's embark on an enriching journey through the vibrant tapestry of news and stories that define Zambia.",
        f"Welcome, welcome! It's a pleasure to have you join us today for the {episode_number} installment of the Zed News Podcast! I'm {podcast_host}, your friendly guide through the ever-evolving news landscape of Zambia. Get ready to immerse yourself in the latest headlines and captivating narratives that await us.",
        f"Here we are, on {today_human_readable}, marking the {episode_number} edition of the Zed News Podcast! I'm {podcast_host}, your enthusiastic host, and I'm delighted to have you with us as we traverse the vast expanse of news and stories that illuminate the heart of Zambia.",
    ]

    return random.choice(data)


def random_intro():
    data = [
        "Whether you're commuting, relaxing at home, or going about your day, the Zed News Podcast is designed to keep you informed and engaged. We know your time is valuable, so we'll deliver the news in a concise yet captivating format, allowing you to stay updated without feeling overwhelmed.",
        "In today's episode, we'll dive into the headlines making waves across Zambia. Sit back, relax, and let's explore the stories that shape our nation.",
        "As we delve into the news landscape, we'll bring you a curated selection of the most important stories from various sources. Stay tuned for a brief overview of what's happening in Zambia.",
        "Join us on this informative journey as we uncover the latest developments and provide you with a snapshot of the events happening around Zambia and beyond.",
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
        "Time to embark on our news journey. Let's dive right in.",
    ]

    return random.choice(variations)


def random_outro():
    variations = [
        f"And that, dear listeners, brings us to the end of another fantastic edition of the 'Zed News Podcast'. I hope you enjoyed our time together today, catching up on the latest happenings. Until next time, this is {podcast_host} signing off, wishing you a wonderful day or night ahead. Take care, stay safe, and keep being awesome. Later!",
        f"And with that, we come to the conclusion of another captivating edition of the 'Zed News Podcast'. I hope you found our exploration of the news landscape insightful and illuminating. Until we meet again, this is {podcast_host} bidding you farewell, wishing you a remarkable day or night. Stay informed, and keep making a difference. Goodbye, everyone!",
        f"That brings us to the end of this remarkable episode of the 'Zed News Podcast'. I trust you found our discussion enlightening and thought-provoking. Until next time, this is {podcast_host}, your host, signing off. Take care and see ypou later!",
        f"And with that, we wrap up another exciting edition of the 'Zed News Podcast'. I hope you enjoyed our time together, staying up to date with the latest news. Until we reconvene, this is {podcast_host}, your friendly voice in the news, saying farewell. Bye for now!",
        f"That concludes our journey through this edition of the 'Zed News Podcast'. I trust you found our exploration of the news landscape insightful and illuminating. Until our paths cross again, this is {podcast_host}, your guide in the realm of information, bidding you adieu. Bye bye for now!",
        f"And so, we reach the end of another remarkable episode of the 'Zed News Podcast'. I hope you found our curation and storytelling captivating and informative. Until we meet again, this is {podcast_host}, your companion on the news adventure, signing off. May your day or night be filled with meaningful connections, profound discoveries, and a commitment to positive change. God willing, tizaonana mailo!",
        f"That brings us to the conclusion of this edition of the 'Zed News Podcast'. I hope you enjoyed our exploration of the news landscape and gained valuable insights. Until our paths cross again, this is {podcast_host}, your friendly host, bidding you farewell. Goodbye folks!",
    ]
    return random.choice(variations)


async def create_transcript(news: list[dict[str, str]], dest: str):
    """Create a podcast transcript from the news, and write it to a file

    Steps:
    1. categorize the news by source
    2. write a brief intro welcoming the listener to the podcast
    3. for each source:
        - mention that we're reading from the source
        - for each news item:
            - read the title
            - if item has category, specify that it was posted in that category
            - read the content
    4. write a brief outro thanking the listener for listening to the podcast
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
            read += (
                f", which has an astounding {article_count} entries today! Let's try and go through them quickly.\n\n"
            )
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

            # =============== Summarize using OpenAI ===============
            # logging.info(f"Summarizing '{title}' via Cohere ...")
            # # https://docs.cohere.com/reference/summarize-2
            # response = co.summarize(
            #     text=content,
            #     model="summarize-xlarge",
            #     temperature=0.5,
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