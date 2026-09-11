import json
import logging
from datetime import datetime, timedelta

from app.core.db.models import Article
from app.core.news.historical import fetch_all
from app.core.news.rss_sources import get_rss_feed_entries
from app.core.news.znbc import get_news
from app.core.summarization.embeddings import embed_text
from app.core.utilities import is_backfill, today


def get_latest_news() -> list[dict[str, str]]:
    """Fetches news for the target date from all sources.

    For today, this hits each source's live feed/listing. For a backfilled
    date (ZED_NEWS_DATE set to a past day), it instead walks each source's
    own archive, since live feeds only carry a rolling window of recent
    items. ZNBC and MUVI TV have no reliable archive, so they're skipped
    when backfilling.
    """
    if is_backfill:
        logging.info(f"Backfilling news for {today.isoformat()} ...")
        since = datetime(today.year, today.month, today.day)
        return fetch_all(since, until=since + timedelta(days=1))

    logging.info("Fetching news from ZNBC ...")
    news = get_news()

    logging.info("Fetching feeds from the other sources ...")
    feeds = get_rss_feed_entries()

    return feeds + news


def save_news_to_db(news: list[dict[str, str]]) -> dict[str, Article]:
    """Saves the news to the database, keyed by URL.

    The URL keying lets callers look up each item's saved row afterwards (e.g. to run
    story continuity retrieval against its embedding - see STORY_CONTINUITY_PLAN.md
    Phase 4) without a second query or relying on list order surviving downstream
    regrouping.
    """

    logging.info("Saving news to the database ...")

    return {item["url"]: Article.create(**item, embedding=embed_text(item["content"])) for item in news}


def save_news_to_file(news: list[dict[str, str]], dest: str):
    """Saves the news to a JSON file"""

    logging.info("Saving news to a JSON file ...")

    with open(dest, "w") as json_file:
        json.dump(news, json_file, indent=2, ensure_ascii=False)
