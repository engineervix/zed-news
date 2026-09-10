"""Fetches articles from a source's own archive rather than its live feed/listing.

Three of the four RSS sites expose the standard WordPress REST API, which
gives real publish dates and full content directly - no per-site HTML
guessing needed. Mwebantu blocks its REST API (403), so it falls back to
scraping its story-row listing and reusing get_mwebantu_article_detail
for content, checking each candidate's own page for its published-date
meta tag since the listing itself carries no usable date.

ZNBC has no reliable archive to walk: its listing pagination isn't
consistently sorted by date, so it stays live-feed-only.
"""

import html
import logging
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from app.core.news.rss_sources import get_mwebantu_article_detail, ua

logger = logging.getLogger(__name__)

REST_SOURCES = {
    "News Diggers!": "https://diggers.news",
    "Zambia Daily Mail": "http://www.daily-mail.co.zm",
    "Times of Zambia": "https://times.co.zm",
}


def _plain_text(content_html: str) -> str:
    soup = BeautifulSoup(content_html, "html.parser")
    for paywall in soup.select(".pmpro"):
        paywall.decompose()
    return "\n".join(p.get_text(strip=True) for p in soup.find_all("p"))


def fetch_wp_rest_posts(
    source: str, base_url: str, since: datetime, until: datetime | None = None, max_pages: int = 5
) -> list[dict[str, str]]:
    """Fetch WordPress posts published in [since, until), via the site's own REST API.

    Args:
        source: The article dict's `source` value, e.g. "News Diggers!".
        base_url: The site's root URL, with no trailing slash, e.g. "https://diggers.news".
        since: Stop once a page's newest-first posts reach one older than this.
        until: Skip posts published on or after this (open backlog when None).
        max_pages: Upper bound on how many pages of 100 posts to walk back through.

    Returns:
        Article dicts with `source`, `url`, `title`, `content`, and `category` keys.
    """
    articles = []
    page = 1
    while page <= max_pages:
        try:
            response = requests.get(
                f"{base_url}/wp-json/wp/v2/posts",
                params={"per_page": 100, "page": page},
                headers={"User-Agent": ua.chrome},
                timeout=20,
            )
        except requests.exceptions.RequestException:
            logger.error(f"Failed to fetch {source} page {page}", exc_info=True)
            break
        if response.status_code != 200:
            break

        posts = response.json()
        if not posts:
            break

        reached_cutoff = False
        for post in posts:
            published = datetime.fromisoformat(post["date"])
            if published < since:
                # wp-json/wp/v2/posts defaults to newest-first, so nothing
                # after this point (this page or later ones) is in range
                reached_cutoff = True
                break
            if until is not None and published >= until:
                continue
            content = _plain_text(post["content"]["rendered"])
            if not content:
                continue
            articles.append(
                {
                    "source": source,
                    "url": post["link"],
                    "title": html.unescape(post["title"]["rendered"]),
                    "content": content,
                    "category": "",
                }
            )

        total_pages = int(response.headers.get("X-WP-TotalPages", page))
        if reached_cutoff or page >= total_pages:
            break
        page += 1
        time.sleep(1.5)

    return articles


def _classify_mwebantu_article(
    title: str, link: str, since: datetime, until: datetime | None
) -> tuple[dict[str, str] | None, bool]:
    """Fetch one Mwebantu article and classify it against [since, until).

    Returns (article dict or None, reached_cutoff). reached_cutoff is True
    only when this article is older than `since`, the signal that a page's
    walk has gone far enough back regardless of how many articles on the
    page actually landed in the window.
    """
    try:
        detail = requests.get(link, headers={"User-Agent": ua.chrome}, timeout=20)
    except requests.exceptions.RequestException:
        logger.error(f"Failed to fetch Mwebantu article {link}", exc_info=True)
        return None, False

    detail_soup = BeautifulSoup(detail.text, "html.parser")
    meta = detail_soup.find("meta", property="article:published_time")
    if not meta or not meta.get("content"):
        return None, False
    published = datetime.fromisoformat(meta["content"]).replace(tzinfo=None)

    if published < since:
        return None, True
    if until is not None and published >= until:
        return None, False

    content = get_mwebantu_article_detail(link)
    if not content:
        return None, False
    return {"source": "Mwebantu", "url": link, "title": title, "content": content, "category": ""}, False


def fetch_mwebantu_backlog(since: datetime, until: datetime | None = None, max_pages: int = 6) -> list[dict[str, str]]:
    """Fetch Mwebantu posts published in [since, until).

    Mwebantu blocks its REST API, so this walks its listing pages instead
    and checks each candidate article's own page for a published-date tag,
    since the listing itself carries no date.

    Args:
        since: Skip any article whose published-date tag is older than this.
        until: Skip articles published on or after this (open backlog when None).
        max_pages: Upper bound on how many listing pages to walk back through.

    Returns:
        Article dicts with `source`, `url`, `title`, `content`, and `category` keys.
    """
    articles = []
    for page in range(1, max_pages + 1):
        url = "https://www.mwebantu.com/" if page == 1 else f"https://www.mwebantu.com/page/{page}/"
        try:
            response = requests.get(url, headers={"User-Agent": ua.chrome}, timeout=20)
        except requests.exceptions.RequestException:
            logger.error(f"Failed to fetch Mwebantu page {page}", exc_info=True)
            break
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        candidates = {(a.get_text(strip=True), a["href"]) for a in soup.select("article.m26-story-row h3 a[href]")}
        if not candidates:
            break

        page_articles = []
        reached_cutoff = False
        for title, link in candidates:
            time.sleep(1.5)
            article, is_cutoff = _classify_mwebantu_article(title, link, since, until)
            if article:
                page_articles.append(article)
            reached_cutoff = reached_cutoff or is_cutoff

        articles += page_articles
        if reached_cutoff:
            break

    return articles


def fetch_all(since: datetime, until: datetime | None = None) -> list[dict[str, str]]:
    """Fetch the historical backlog across the archivable sites, for [since, until)."""
    articles = []
    for source, base_url in REST_SOURCES.items():
        articles += fetch_wp_rest_posts(source, base_url, since, until=until)
    articles += fetch_mwebantu_backlog(since, until=until)
    return articles
