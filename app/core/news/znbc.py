#!/usr/bin/env python3
"""
Fetches today's news from https://www.znbc.co.zm/news/
"""

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from app.core.utilities import today_iso_fmt

ua = UserAgent(
    fallback="Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_5; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.204",
)


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


def get_news():
    """
    Fetches today's news from https://www.znbc.co.zm/news/
    """
    url = "https://www.znbc.co.zm/news/"
    headers = {"User-Agent": ua.random}
    response = requests.get(url, headers=headers, timeout=60)
    soup = BeautifulSoup(response.text, "html.parser")
    news = soup.find_all("article")
    latest_news = []
    encountered_titles = set()
    # Skip the first item because it seems to be
    # all the news articles wrapped in an article tag
    for article in reversed(news[1:]):
        time_element = article.find("time", class_="entry-date")
        if time_element and time_element.get("datetime") and time_element.get("datetime").startswith(today_iso_fmt):
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
                        "source": "Zambia National Broadcasting Corporation (ZNBC)",
                        "url": detail_url,
                        "title": title,
                        "content": content,
                        "category": category,
                        # "author": author,
                    }
                )

                # Add title to encountered titles set
                encountered_titles.add(title)

    return latest_news[::-1]


# if __name__ == "__main__":
#     with open(f"data/_znbc_news_{today_iso_fmt}.json", "w") as json_file:
#         json.dump(fetch_news(), json_file, indent=2, ensure_ascii=False)
