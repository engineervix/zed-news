import json
import logging

from app.core.db.models import Article
from app.core.news.other import get_rss_feed_entries
from app.core.news.znbc import get_news


def get_latest_news():
    """Fetches today's news from all sources"""

    logging.info("Fetching news from ZNBC ...")
    news = get_news()

    logging.info("Fetching feeds from the other sources ...")
    feeds = get_rss_feed_entries()

    return feeds + news


async def save_news_to_db(news: list[dict[str, str]]):
    """Saves the news to the database"""

    logging.info("Saving news to the database ...")

    for item in news:
        await Article.create(**item)


def save_news_to_file(news: list[dict[str, str]], dest: str):
    """Saves the news to a JSON file"""

    logging.info("Saving news to a JSON file ...")

    with open(dest, "w") as json_file:
        json.dump(news, json_file, indent=2, ensure_ascii=False)
