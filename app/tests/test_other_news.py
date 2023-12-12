import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from urllib.parse import urlparse

from feedparser.util import FeedParserDict

from app.core.news.other import (
    URLs,
    get_daily_mail_article_detail,
    get_description,
    get_diggers_article_detail,
    get_feed_title,
    get_muvitv_article_detail,
    get_mwebantu_article_detail,
)

# from app.core.news.other import get_rss_feed_entries,


def mock_parse(url, *args, **kwargs):
    """
    Mocks the feedparser.parse() function to return a mock feed
    based on the specified URL
    """
    utc_dt = datetime.now(timezone.utc)
    if url in URLs:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return FeedParserDict(
            {
                "feed": {
                    "title": "Test Feed",
                    "link": base_url,
                    "updated": utc_dt.strftime("%a, %d %b %Y %H:%M:%S %Z"),
                },
                "updated": utc_dt.strftime("%a, %d %b %Y %H:%M:%S %Z"),
                "encoding": "UTF-8",
                "entries": [
                    {
                        "link": f"{base_url}/article1",
                        "title": "Article 1",
                        "published": utc_dt.strftime("%a, %d %b %Y %H:%M:%S %Z"),
                    },
                    {
                        "link": f"{base_url}/article2",
                        "title": "Article 2",
                        "published": utc_dt.strftime("%a, %d %b %Y %H:%M:%S %Z"),
                    },
                ],
            }
        )
    else:
        return FeedParserDict(
            {
                "feed": {
                    "title": "Example Feed",
                    "link": "https://example.com",
                    "updated": utc_dt.strftime("%a, %d %b %Y %H:%M:%S %Z"),
                },
                "updated": utc_dt.strftime("%a, %d %b %Y %H:%M:%S %Z"),
                "encoding": "UTF-8",
                "entries": [
                    {
                        "link": "https://example.com/article1",
                        "title": "Article 1",
                        "published": utc_dt.strftime("%a, %d %b %Y %H:%M:%S %Z"),
                    },
                    {
                        "link": "https://example.com/article2",
                        "title": "Article 2",
                        "published": utc_dt.strftime("%a, %d %b %Y %H:%M:%S %Z"),
                    },
                ],
            }
        )


class TestOtherNews(unittest.TestCase):
    def setUp(self):
        self.daily_mail_url = "http://www.daily-mail.co.zm/article"
        self.mwebantu_url = "https://www.mwebantu.com/article"
        self.muvitv_url = "https://www.muvitv.com/article"
        self.diggers_url = "https://diggers.news/article"
        self.invalid_url = "http://www.example.com/invalid"

    @patch("app.core.news.other.requests.get")
    def test_get_daily_mail_article_detail(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <article>
                    <div class="entry-content">
                        <p>Paragraph 1.</p>
                        <p>Paragraph 2.</p>
                    </div>
                </article>
            </body>
        </html>
        """

        mock_get.return_value = mock_response

        article_detail = get_daily_mail_article_detail(self.daily_mail_url)
        self.assertEqual(article_detail, "Paragraph 1.\nParagraph 2.")

    @patch("app.core.news.other.requests.get")
    def test_get_mwebantu_article_detail(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <article>
                    <div class="theiaPostSlider_preloadedSlide">
                        <p>Paragraph 1.</p>
                        <p>Paragraph 2.</p>
                    </div>
                </article>
            </body>
        </html>
        """
        mock_get.return_value = mock_response

        article_detail = get_mwebantu_article_detail(self.mwebantu_url)
        self.assertEqual(article_detail, "Paragraph 1.\nParagraph 2.")

    @patch("app.core.news.other.requests.get")
    def test_get_muvitv_article_detail(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <article>
                    <div class="tdb_single_content">
                        <p>Paragraph 0.</p>
                        <p>Paragraph 1.</p>
                    </div>
                </article>
            </body>
        </html>
        """

        mock_get.return_value = mock_response

        article_detail = get_muvitv_article_detail(self.muvitv_url)
        self.assertEqual(article_detail, "Paragraph 0.\nParagraph 1.")

    @patch("app.core.news.other.requests.get")
    def test_get_diggers_article_detail(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <div class="article-text">
                    <p>Paragraph 0.</p>
                    <p>Paragraph 1.</p>
                </div>
            </body>
        </html>
        """

        mock_get.return_value = mock_response

        article_detail = get_diggers_article_detail(self.diggers_url)
        self.assertEqual(article_detail, "Paragraph 0.\nParagraph 1.")

    @patch("app.core.news.other.get_daily_mail_article_detail")
    @patch("app.core.news.other.get_mwebantu_article_detail")
    @patch("app.core.news.other.get_muvitv_article_detail")
    @patch("app.core.news.other.get_diggers_article_detail")
    @patch("app.core.news.other.requests.get")
    def test_get_description(self, mock_get, mock_diggers, mock_muvitv, mock_mwebantu, mock_daily_mail):
        mock_daily_mail.return_value = "Daily Mail Article content"
        mock_mwebantu.return_value = "Mwebantu Article content"
        mock_muvitv.return_value = "Muvi TV Article content"
        mock_diggers.return_value = "Diggers News Article content"

        # Daily Mail
        description = get_description(self.daily_mail_url)
        self.assertEqual(description, "Daily Mail Article content")

        # Mwebantu
        description = get_description(self.mwebantu_url)
        self.assertEqual(description, "Mwebantu Article content")

        # Muvi TV
        description = get_description(self.muvitv_url)
        self.assertEqual(description, "Muvi TV Article content")

        # Diggers News
        description = get_description(self.diggers_url)
        self.assertEqual(description, "Diggers News Article content")

        # Invalid URL
        mock_response = MagicMock()
        mock_response.text = "<html><body>Invalid URL</body></html>"
        mock_get.return_value = mock_response

        description = get_description(self.invalid_url)
        self.assertIsNone(description)

    def test_get_feed_title(self):
        # Daily Mail
        feed_title = get_feed_title(self.daily_mail_url)
        self.assertEqual(feed_title, "Zambia Daily Mail")

        # Mwebantu
        feed_title = get_feed_title(self.mwebantu_url)
        self.assertEqual(feed_title, "Mwebantu")

        # Muvi TV
        feed_title = get_feed_title(self.muvitv_url)
        self.assertEqual(feed_title, "MUVI Television")

        # Diggers News
        feed_title = get_feed_title(self.diggers_url)
        self.assertEqual(feed_title, "News Diggers!")

        # Invalid URL
        feed_title = get_feed_title(self.invalid_url)
        self.assertIsNone(feed_title)

    # @patch("app.core.news.other.get_description")
    # @patch("app.core.news.other.feedparser.parse", return_value=MagicMock())
    # def test_get_rss_feed_entries(self, mock_feedparser_parse, mock_get_description):
    #     mock_feedparser_parse.side_effect = [mock_parse(url) for url in URLs]
    #     mock_get_description.return_value = "Article content"

    #     result = get_rss_feed_entries()

    #     self.assertEqual(len(result), 4)

    #     for item, url in zip(result, URLs, strict=True):
    #         parsed_url = urlparse(url)
    #         base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    #         self.assertEqual(item["source"], get_feed_title(url))
    #         self.assertEqual(item["url"], f"{base_url}/article1")
    #         self.assertEqual(item["title"], "Article 1")
    #         self.assertEqual(item["content"], "Article content")
    #         self.assertEqual(item["category"], "")


if __name__ == "__main__":
    unittest.main()
