"""Historical article backlog for the DSPy eval fixture.

Three of the four sites expose the standard WordPress REST API, which
gives real publish dates and full content directly - no per-site HTML
guessing needed. Mwebantu blocks its REST API (403), so it falls back to
scraping its story-row listing and reusing get_mwebantu_article_detail
for content, checking each candidate's own page for its published-date
meta tag since the listing itself carries no usable date.

Dev-only, matches fetch_eval_articles.py's fixture path and gitignore
policy: real news, not committed, regenerate locally when needed.
"""

import html
import logging
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from app.core.news.other import get_mwebantu_article_detail, ua

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


def fetch_wp_rest_posts(source: str, base_url: str, since: datetime, max_pages: int = 5) -> list[dict[str, str]]:
    """Fetch WordPress posts published since a cutoff, via the site's own REST API.

    Args:
        source: The article dict's `source` value, e.g. "News Diggers!".
        base_url: The site's root URL, with no trailing slash, e.g. "https://diggers.news".
        since: Stop once a page's newest-first posts reach one older than this.
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


def _fetch_recent_mwebantu_article(title: str, link: str, since: datetime) -> dict[str, str] | None:
    """Fetch one Mwebantu article if its published-date meta tag is within the cutoff."""
    try:
        detail = requests.get(link, headers={"User-Agent": ua.chrome}, timeout=20)
    except requests.exceptions.RequestException:
        logger.error(f"Failed to fetch Mwebantu article {link}", exc_info=True)
        return None

    detail_soup = BeautifulSoup(detail.text, "html.parser")
    meta = detail_soup.find("meta", property="article:published_time")
    if not meta or not meta.get("content"):
        return None
    published = datetime.fromisoformat(meta["content"]).replace(tzinfo=None)
    if published < since:
        return None

    content = get_mwebantu_article_detail(link)
    if not content:
        return None
    return {"source": "Mwebantu", "url": link, "title": title, "content": content, "category": ""}


def fetch_mwebantu_backlog(since: datetime, max_pages: int = 6) -> list[dict[str, str]]:
    """Fetch Mwebantu posts published since a cutoff.

    Mwebantu blocks its REST API, so this walks its listing pages instead
    and checks each candidate article's own page for a published-date tag,
    since the listing itself carries no date.

    Args:
        since: Skip any article whose published-date tag is older than this.
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
        for title, link in candidates:
            time.sleep(1.5)
            article = _fetch_recent_mwebantu_article(title, link, since)
            if article:
                page_articles.append(article)

        if not page_articles:
            break
        articles += page_articles

    return articles


def fetch_all(since: datetime) -> list[dict[str, str]]:
    """Fetch the historical backlog across all four sites, since a cutoff date."""
    articles = []
    for source, base_url in REST_SOURCES.items():
        articles += fetch_wp_rest_posts(source, base_url, since)
    articles += fetch_mwebantu_backlog(since)
    return articles
