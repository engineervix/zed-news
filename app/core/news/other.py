import logging
import traceback
from http import HTTPStatus
from urllib.parse import urlparse, urlunparse

import dateutil.parser
import feedparser
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from app.core.utilities import today_iso_fmt

logger = logging.getLogger(__name__)

ua = UserAgent(
    fallback="Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_5; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.204",
)

URLs = [
    "http://www.daily-mail.co.zm/feed/",
    "https://diggers.news/rss/",
    "https://www.muvitv.com/rss/",
    "https://www.mwebantu.com/rss/",
    "https://www.times.co.zm/?feed=rss2",
]


def get_daily_mail_article_detail(url):
    """
    Fetches the article detail from a Zambia Daily Mail URL
    """
    if "daily-mail.co.zm" not in url:
        logger.error(f"{url} is not a Zambia Daily Mail URL")
        return None
    else:
        parsed_url = urlparse(url)
        # Create a new URL without query parameters
        new_url = urlunparse(parsed_url._replace(query=""))

        response = requests.get(new_url)
        soup = BeautifulSoup(response.text, "html.parser")
        if article := soup.find("article"):
            content_element = article.select_one("div.entry-content")
            paragraphs = content_element.find_all("p")
            content = "\n".join([p.get_text() for p in paragraphs])

            # Remove "CLICK TO READ MORE" from the content
            content = content.replace("CLICK TO READ MORE", "...")
            content = content.replace("https://enews.daily-mail.co.zm/welcome/home", "")

            # remove Read more: eNews Daily Mail | Without Fear Or Favour (daily-mail.co.zm)
            content = content.replace("Read more: eNews Daily Mail | Without Fear Or Favour (daily-mail.co.zm)", "")

            return content
        elif article := soup.find("main"):
            content_elements = article.select("div.e-con-inner")
            content_element = content_elements[-1]
            paragraphs = content_element.find_all("p")
            content = "\n".join([p.get_text() for p in paragraphs])

            # remove Read more: eNews Daily Mail | Without Fear Or Favour (daily-mail.co.zm)
            content = content.replace("Read more: eNews Daily Mail | Without Fear Or Favour (daily-mail.co.zm)", "")

            # Remove "CLICK TO READ MORE" from the content
            content = content.replace("CLICK TO READ MORE", "...")
            content = content.replace("https://enews.daily-mail.co.zm/welcome/home", "")

            return content
        return None


def get_times_of_zambia_article_detail(url):
    """
    Fetches the article detail from a Times of Zambia URL
    """
    if "times.co.zm" not in url:
        logger.error(f"{url} is not a Times of Zambia URL")
        return None
    else:
        response = requests.get(url)

        if response.status_code != HTTPStatus.OK:
            logger.error(f"Failed to fetch the article from {url}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        article_content = soup.find("div", class_="single-content")

        if not article_content:
            logger.error("No article content found")
            return None

        # Remove any 'Read more' links
        for read_more in article_content.find_all("a", string="Read more"):
            read_more.decompose()

        # Extract text from paragraphs
        paragraphs = article_content.find_all("p")
        text_content = "\n".join(p.get_text() for p in paragraphs)

        return text_content.strip()


def get_mwebantu_article_detail(url):
    """
    Fetches the article detail from a Mwebantu URL
    """
    if "mwebantu.com" not in url:
        logger.error(f"{url} is not a Mwebantu URL")
        return None
    else:
        parsed_url = urlparse(url)
        # Create a new URL without query parameters
        new_url = urlunparse(parsed_url._replace(query=""))

        response = requests.get(new_url)
        soup = BeautifulSoup(response.text, "html.parser")

        article = soup.find("article")
        if article:
            content_element = article.select_one("div.theiaPostSlider_preloadedSlide")
            paragraphs = content_element.find_all("p")

            # Remove "(Mwebantu ...)" from the content
            content_lines = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
            if content_lines and content_lines[-1].startswith("(Mwebantu, "):
                content_lines.pop()

            content = "\n".join(content_lines)
        else:
            content = None

        return content


def get_muvitv_article_detail(url):
    """
    Fetches the article detail from a Muvi TV URL
    """
    if "muvitv.com" not in url:
        logger.error(f"{url} is not a Muvi TV URL")
        return None
    else:
        parsed_url = urlparse(url)
        # Create a new URL without query parameters
        new_url = urlunparse(parsed_url._replace(query=""))

        response = requests.get(new_url)
        soup = BeautifulSoup(response.text, "html.parser")

        article = soup.find("article")

        if article:
            content_element = article.select_one("div.tdb_single_content")
            paragraphs = content_element.find_all("p")

            content = "\n".join([p.get_text(strip=True) for p in paragraphs])
        else:
            content = None

        return content


def get_diggers_article_detail(url):
    """
    Fetches the article detail from a Diggers News URL
    """
    if "diggers.news" not in url:
        logger.error(f"{url} is not a Diggers News URL")
        return None
    elif url.startswith("https://diggers.news/cartoons"):
        logger.error(f"{url} points to a cartoon image. Skipping.")
        return None
    else:
        parsed_url = urlparse(url)
        # Create a new URL without query parameters
        new_url = urlunparse(parsed_url._replace(query=""))

        response = requests.get(new_url)
        soup = BeautifulSoup(response.text, "html.parser")

        article = soup.select_one("div.article-text")

        if article:
            paragraphs = article.find_all("p")

            content = "\n".join([p.get_text(strip=True) for p in paragraphs])
        else:
            content = None

        return content


def get_description(url):
    """
    Fetches the article detail from a URL
    """
    if "daily-mail.co.zm" in url:
        return get_daily_mail_article_detail(url)
    if "times.co.zm" in url:
        return get_times_of_zambia_article_detail(url)
    elif "mwebantu.com" in url:
        return get_mwebantu_article_detail(url)
    elif "muvitv.com" in url:
        return get_muvitv_article_detail(url)
    elif "diggers.news" in url:
        return get_diggers_article_detail(url)
    else:
        return None


def get_feed_title(url):
    """
    Fetches the feed title from a URL
    """
    if "daily-mail.co.zm" in url:
        return "Zambia Daily Mail"
    if "times.co.zm" in url:
        return "Times of Zambia"
    elif "mwebantu.com" in url:
        return "Mwebantu"
    elif "muvitv.com" in url:
        return "MUVI Television"
    elif "diggers.news" in url:
        return "News Diggers!"
    else:
        return None


def get_rss_feed_entries():
    """
    Parses URLs and fetches today's feeds

    TODO: This is a poor implementation - everything breaks if something goes wrong
    when fetching article content. We need to refactor this to handle errors better.
    """

    try:
        feeds = [
            feedparser.parse(
                url,
                request_headers={"User-Agent": ua.chrome, "Cache-Control": "max-age=0"},
            )
            for url in URLs
        ]
        feed = [item for feed in feeds for item in feed.entries]

        return [
            {
                "source": get_feed_title(i["link"]),
                "url": i["link"],
                "title": i["title"],
                "content": get_description(i["link"]),
                "category": "",
                # "published": i["published"],
            }
            for i in feed
            if i.get("published")
            and dateutil.parser.parse(i["published"]).date().isoformat() == today_iso_fmt
            and get_description(i["link"])
        ]
    except Exception:
        logger.error(traceback.format_exc())
        return []
