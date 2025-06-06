"""
Toolchain for fetching news content and processing it into a digest.
"""

import json
import logging
import subprocess
import time

from colorama import init
from dotenv import load_dotenv

from app.core.db.config import close_database, initialize_database
from app.core.news.digest import create_news_digest
from app.core.news.eleventify import render_jinja_template
from app.core.news.fetch import get_latest_news, save_news_to_db, save_news_to_file
from app.core.summarization.backends import together as together_backend
from app.core.utilities import DATA_DIR, configure_logging, today_iso_fmt

raw_news = f"{DATA_DIR}/{today_iso_fmt}_news.json"
digest_content = f"{DATA_DIR}/{today_iso_fmt}_digest-content.txt"
digest_metadata = f"{DATA_DIR}/{today_iso_fmt}_digest.json"


def _read_json_file(file):
    with open(file) as f:
        return json.load(f)


def main():
    start_time = time.time()

    # Configure logging
    init()
    configure_logging()

    # Load environment variables
    load_dotenv()

    # Fetch news
    logging.info("Fetching latest news from all sources...")
    news = get_latest_news()

    # Save news to a JSON file
    save_news_to_file(news, raw_news)

    # news = _read_json_file(raw_news)  # for testing

    # Connect to the database
    initialize_database()

    # Save news to the database
    save_news_to_db(news)

    # Create news digest
    logging.info("Creating news digest...")
    digest_data = create_news_digest(news, digest_content, together_backend.summarize)

    end_time = time.time()
    processing_time = int(end_time - start_time)

    # Add processing metadata to digest data
    digest_data.update(
        {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "raw_news_file": raw_news,
            "digest_file": digest_content,
        }
    )

    # Save digest metadata to JSON file for website generation
    with open(digest_metadata, "w") as f:
        json.dump(digest_data, f, indent=2, ensure_ascii=False)

    logging.info(f"News digest processing completed in {processing_time} seconds")
    logging.info(f"Digest metadata saved to: {digest_metadata}")

    # Move files to today's directory for organization first
    # NOTE: Run a cron job to delete these files after a month
    subprocess.run(
        f"mkdir -p {DATA_DIR}/{today_iso_fmt}",
        shell=True,
    )
    subprocess.run(
        f"mv -v {digest_content} {DATA_DIR}/{today_iso_fmt}/",
        shell=True,
    )
    subprocess.run(
        f"mv -v {raw_news} {DATA_DIR}/{today_iso_fmt}/",
        shell=True,
    )
    subprocess.run(
        f"mv -v {digest_metadata} {DATA_DIR}/{today_iso_fmt}/",
        shell=True,
    )

    # Render the Jinja template for website generation (after files are moved)
    render_jinja_template()

    logging.info("News digest generation completed successfully!")

    # Close the database connection
    close_database()


if __name__ == "__main__":
    main()
