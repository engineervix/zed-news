import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.core.summarization.backends.fetch_historical_articles import (
    _plain_text,
    fetch_mwebantu_backlog,
    fetch_wp_rest_posts,
)

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


class TestPlainText(unittest.TestCase):
    """Test cases for stripping paywall markup and extracting paragraph text"""

    def test_extracts_paragraphs_and_strips_paywall(self):
        content_html = (
            "<p>First paragraph.</p><p>Second paragraph.</p>"
            '<div class="pmpro"><p>Subscribe to keep reading.</p></div>'
        )

        result = _plain_text(content_html)

        self.assertEqual(result, "First paragraph.\nSecond paragraph.")


class TestFetchWpRestPosts(unittest.TestCase):
    """Test cases for fetching historical articles via the WordPress REST API"""

    @patch("app.core.summarization.backends.fetch_historical_articles.requests.get")
    def test_filters_by_date_and_builds_articles(self, mock_get):
        response = MagicMock()
        response.status_code = 200
        response.headers = {"X-WP-TotalPages": "1"}
        response.json.return_value = [
            {
                "date": "2026-08-30T10:00:00",
                "link": "https://example.com/recent",
                "title": {"rendered": "Recent &amp; Newsworthy"},
                "content": {"rendered": "<p>Recent content.</p>"},
            },
            {
                "date": "2026-08-01T10:00:00",
                "link": "https://example.com/old",
                "title": {"rendered": "Old story"},
                "content": {"rendered": "<p>Old content.</p>"},
            },
        ]
        mock_get.return_value = response

        articles = fetch_wp_rest_posts("Example News", "https://example.com", since=datetime(2026, 8, 25))

        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["title"], "Recent & Newsworthy")
        self.assertEqual(articles[0]["content"], "Recent content.")
        self.assertEqual(articles[0]["source"], "Example News")
        self.assertEqual(articles[0]["url"], "https://example.com/recent")

    @patch("app.core.summarization.backends.fetch_historical_articles.requests.get")
    def test_stops_when_no_posts_returned(self, mock_get):
        response = MagicMock()
        response.status_code = 200
        response.headers = {"X-WP-TotalPages": "5"}
        response.json.return_value = []
        mock_get.return_value = response

        articles = fetch_wp_rest_posts("Example News", "https://example.com", since=datetime(2026, 8, 25))

        self.assertEqual(articles, [])
        mock_get.assert_called_once()

    @patch("app.core.summarization.backends.fetch_historical_articles.requests.get")
    def test_stops_paginating_once_a_post_is_older_than_the_cutoff(self, mock_get):
        response = MagicMock()
        response.status_code = 200
        response.headers = {"X-WP-TotalPages": "148"}
        response.json.return_value = [
            {
                "date": "2026-08-01T10:00:00",
                "link": "https://example.com/old",
                "title": {"rendered": "Old story"},
                "content": {"rendered": "<p>Old content.</p>"},
            }
        ]
        mock_get.return_value = response

        articles = fetch_wp_rest_posts("Example News", "https://example.com", since=datetime(2026, 8, 25))

        self.assertEqual(articles, [])
        mock_get.assert_called_once()


class TestFetchMwebantuBacklog(unittest.TestCase):
    """Test cases for fetching historical Mwebantu articles via listing-page scraping"""

    @patch("app.core.summarization.backends.fetch_historical_articles.time.sleep")
    @patch("app.core.summarization.backends.fetch_historical_articles.get_mwebantu_article_detail")
    @patch("app.core.summarization.backends.fetch_historical_articles.requests.get")
    def test_uses_real_listing_structure(self, mock_get, mock_get_detail, mock_sleep):
        listing_html = (FIXTURES_DIR / "mwebantu_listing_snippet.html").read_text()
        listing_response = MagicMock(status_code=200, text=listing_html)

        recent_detail = MagicMock(status_code=200)
        recent_detail.text = '<meta property="article:published_time" content="2026-08-30T10:00:00+00:00">'

        old_detail = MagicMock(status_code=200)
        old_detail.text = '<meta property="article:published_time" content="2026-08-01T10:00:00+00:00">'

        empty_page = MagicMock(status_code=200, text="<html><body></body></html>")

        def side_effect(url, **kwargs):
            if url == "https://www.mwebantu.com/":
                return listing_response
            if (
                url
                == "https://www.mwebantu.com/hichilema-sworn-in-for-second-term-pledges-jobs-unity-and-self-reliance/"
            ):
                return recent_detail
            if url in (
                "https://www.mwebantu.com/hichilema-extends-unity-hand-to-rivals-after-inauguration/",
                "https://www.mwebantu.com/inauguration-of-president-hakainde-hichilema-2026-3/",
            ):
                return old_detail
            return empty_page

        mock_get.side_effect = side_effect
        mock_get_detail.return_value = "Full article body."

        articles = fetch_mwebantu_backlog(since=datetime(2026, 8, 25))

        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["source"], "Mwebantu")
        self.assertEqual(
            articles[0]["title"], "Hichilema sworn in for second term, pledges jobs, unity and self-reliance"
        )
        self.assertEqual(articles[0]["content"], "Full article body.")


if __name__ == "__main__":
    unittest.main()
