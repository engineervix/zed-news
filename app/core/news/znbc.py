#!/usr/bin/env python3
"""
Fetches today's news from https://znbc.co.zm/?page_id=4187
"""

import logging

import dateutil.parser
import requests
import urllib3
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from app.core.utilities import today_iso_fmt

logger = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ua = UserAgent(
    fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17720",
)


def get_article_detail(url):
    """
    Fetches the article detail from the URL
    """
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        content_element = soup.select_one("div.elementor-widget-theme-post-content")
        if content_element:
            paragraphs = content_element.find_all("p")
            content = "\n".join([p.get_text(strip=True) for p in paragraphs])
            content = content.split("Post Views:")[0].strip()
        else:
            content = None
    except AttributeError as err:
        logger.exception(f"Error fetching article detail for {url}\n: {err}")
        content = None
    return content


def _parse_article(article, encountered_titles):
    """
    Extracts a news item from an article element, or returns None if it
    doesn't belong to today or can't be parsed.
    """
    date_element = article.select_one("span.elementor-post-date")
    if not date_element:
        return None

    try:
        article_date = dateutil.parser.parse(date_element.get_text(strip=True)).date().isoformat()
    except (ValueError, OverflowError):
        return None

    if article_date != today_iso_fmt:
        return None

    title_element = article.select_one("h3.elementor-post__title a")
    if not title_element:
        return None

    title = title_element.get_text(strip=True)
    if title in encountered_titles:
        return None

    detail_url = title_element["href"]
    content = get_article_detail(detail_url)
    if not content:
        return None

    return {
        "source": "Zambia National Broadcasting Corporation (ZNBC)",
        "url": detail_url,
        "title": title,
        "content": content,
        "category": "",
    }


def get_news():
    """
    Fetches today's news from https://znbc.co.zm/?page_id=4187
    """
    url = "https://znbc.co.zm/?page_id=4187"
    headers = {"User-Agent": ua.firefox}

    try:
        response = requests.get(url, headers=headers, timeout=60, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        news = soup.find_all("article", class_="elementor-post")
        latest_news = []
        encountered_titles = set()

        for article in reversed(news):
            item = _parse_article(article, encountered_titles)
            if item:
                latest_news.append(item)
                encountered_titles.add(item["title"])

        return latest_news[::-1]
    except requests.exceptions.ConnectionError as conn_err:
        logger.exception(f"Connection error occurred for {url}\n: {conn_err}")
        return []
    except requests.exceptions.HTTPError as http_err:
        logger.exception(f"HTTP error occurred for {url}\n: {http_err}")
        return []
    except requests.exceptions.RequestException as req_err:
        logger.exception(f"Request error occurred for {url}\n: {req_err}")
        return []
    except Exception as err:
        logger.exception(f"An unexpected error occurred for {url}\n: {err}")
        return []
