"""
Toolchain for fetching news content and processing it into a podcast.
"""
import asyncio
import json

from colorama import init
from dotenv import load_dotenv
from tortoise import Tortoise

from app.core.db.config import init_db
from app.core.news.fetch import get_latest_news, save_news_to_db, save_news_to_file
from app.core.utilities import DATA_DIR, configure_logging, today_iso_fmt

raw_news = f"{DATA_DIR}/{today_iso_fmt}_news.json"
transcript = f"{DATA_DIR}/{today_iso_fmt}_podcast-content.txt"


def _read_json_file(file):
    with open(file) as f:
        return json.load(f)


async def main():
    # Configure logging
    init()
    configure_logging()

    # Load environment variables
    load_dotenv()

    # Fetch news
    # news = get_latest_news()

    # Save news to a JSON file
    # save_news_to_file(news, raw_news)

    news = _read_json_file(raw_news)

    # Connect to the database
    await init_db()

    try:
        # Save news to the database
        # await save_news_to_db(news)

        # Create podcast transcript
        from app.core.podcast.content import create_transcript

        await create_transcript(news, transcript)

    finally:
        # Close database connections
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
