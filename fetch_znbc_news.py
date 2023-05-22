#!/usr/bin/env python3
"""
Fetches today's news from https://www.znbc.co.zm/news/
"""

import datetime
import json

import requests
from bs4 import BeautifulSoup

today = datetime.date.today().isoformat()


def get_article_detail(url):
    """
    Fetches the article detail from the URL
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    article = soup.find("article")

    # Extract article content
    content_element = article.select_one("div.entry-content")
    paragraphs = content_element.find_all("p")
    content = "\n".join([p.get_text(strip=True) for p in paragraphs])

    # Remove "Post Views: number" from the content
    content = content.split("Post Views:")[0].strip()

    return content


def fetch_news():
    """
    Fetches today's news from https://www.znbc.co.zm/news/
    """
    url = "https://www.znbc.co.zm/news/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    news = soup.find_all("article")
    latest_news = []
    encountered_titles = set()
    # Skip the first item because it seems to be
    # all the news articles wrapped in an article tag
    for article in reversed(news[1:]):
        time_element = article.find("time", class_="entry-date")
        if (
            time_element
            and time_element.get("datetime")
            and time_element.get("datetime").startswith(today)
        ):
            # Extract article title
            title_element = article.select_one("h3.entry-title a")
            title = title_element.text.strip()

            if title not in encountered_titles:
                # Extract author
                # author_element = article.select_one("div.author a")
                # author = author_element.text.strip() if author_element else ""

                # Extract detail URL
                detail_url = title_element["href"]

                # Extract category
                category_element = article.select_one("a.category-item")
                category = category_element.text.strip() if category_element else ""

                # Extract article detail
                content = get_article_detail(detail_url)

                latest_news.append(
                    {
                        "title": title,
                        # "author": author,
                        "category": category,
                        "content": content,
                    }
                )

                # Add title to encountered titles set
                encountered_titles.add(title)

    return latest_news[::-1]


if __name__ == "__main__":
    with open(f"znbc_news_{today}.json", "w") as json_file:
        json.dump(fetch_news(), json_file, indent=2)
