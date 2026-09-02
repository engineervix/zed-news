"""Fetch real articles and save them as the local DSPy eval fixture.

Not committed to git (real news, goes stale, gets rescraped). Run with
`invoke fetch-eval-articles` whenever you need fresh eval data.

Includes a one-off variant of the RSS fetch that skips digest.py's
"today only" filter, to get more variety out of a thin eval set. This
is not a real historical archive: the RSS feeds just happen to carry a
short backlog. ZNBC has no such backlog to relax, so it stays today-only.
"""

import json
import logging
import traceback
from datetime import datetime, timedelta

import feedparser

from app.core.news.fetch import get_latest_news
from app.core.news.rss_sources import URLs, get_description, get_feed_title, ua
from app.core.summarization.devtools.fetch_historical_articles import fetch_all
from app.core.summarization.digest import EVAL_ARTICLES_PATH

logger = logging.getLogger(__name__)


def fetch_rss_backlog() -> list[dict[str, str]]:
    """Fetch RSS entries regardless of publish date."""
    try:
        feeds = [
            feedparser.parse(url, request_headers={"User-Agent": ua.chrome, "Cache-Control": "max-age=0"})
            for url in URLs
        ]
        feed = [item for feed in feeds for item in feed.entries]
    except Exception:
        logger.error(traceback.format_exc())
        return []

    entries = []
    for item in feed:
        if not item.get("link") or not item.get("title"):
            continue
        try:
            content = get_description(item["link"])
        except Exception:
            logger.error(f"Failed to fetch article content for {item['link']}\n{traceback.format_exc()}")
            continue
        if not content:
            continue
        entries.append(
            {
                "source": get_feed_title(item["link"]),
                "url": item["link"],
                "title": item["title"],
                "content": content,
                "category": "",
            }
        )
    return entries


def main() -> None:
    """Fetch today's news, the RSS backlog, and the historical backlog, then save them merged."""
    todays_news = get_latest_news()
    rss_backlog = fetch_rss_backlog()
    historical = fetch_all(since=datetime.now() - timedelta(days=7))

    seen_urls = set()
    articles = []
    for batch in (todays_news, rss_backlog, historical):
        for article in batch:
            if article["url"] in seen_urls:
                continue
            seen_urls.add(article["url"])
            articles.append(article)

    EVAL_ARTICLES_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVAL_ARTICLES_PATH.write_text(json.dumps(articles, indent=2, ensure_ascii=False))
    print(f"saved {len(articles)} articles to {EVAL_ARTICLES_PATH}")


if __name__ == "__main__":
    main()
