import unittest
from unittest.mock import MagicMock, call, patch

from app.core.news.znbc import get_article_detail, get_news
from app.core.utilities import TEST_DIR


class TestGetArticleDetail(unittest.TestCase):
    def setUp(self):
        self.url = "https://example.com/article"

    @patch("app.core.news.znbc.requests")
    def test_get_article_detail(self, mock_requests):
        mock_response = MagicMock()
        mock_response.text = """
            <article>
                <div class="entry-content">
                    <p>Paragraph 1</p>
                    <p>Paragraph 2</p>
                </div>
            </article>
        """
        mock_requests.get.return_value = mock_response

        expected_content = "Paragraph 1\nParagraph 2"
        result = get_article_detail(self.url)

        self.assertEqual(result, expected_content)
        mock_requests.get.assert_called_once_with(self.url)

    @patch("app.core.news.znbc.requests")
    def test_get_article_detail_with_post_views(self, mock_requests):
        mock_response = MagicMock()
        mock_response.text = """
            <article>
                <div class="entry-content">
                    <p>Paragraph 1</p>
                    <p>Paragraph 2</p>
                </div>
            </article>
            <p>Post Views: 100</p>
        """
        mock_requests.get.return_value = mock_response

        expected_content = "Paragraph 1\nParagraph 2"
        result = get_article_detail(self.url)

        self.assertEqual(result, expected_content.split("Post Views:")[0].strip())
        mock_requests.get.assert_called_once_with(self.url)


class TestGetNews(unittest.TestCase):
    def setUp(self):
        self.mock_response = MagicMock()
        with open(f"{TEST_DIR}/fixtures/znbc_test_response.html", "r") as f:
            html_content = f.read()
        self.mock_response.text = html_content

    @patch("app.core.news.znbc.requests")
    @patch("app.core.news.znbc.get_article_detail")
    @patch("app.core.news.znbc.ua")
    def test_get_news(self, mock_user_agent, mock_get_article_detail, mock_requests):
        mock_user_agent.random = "Mock User Agent"
        mock_requests.get.return_value = self.mock_response
        mock_get_article_detail.side_effect = [
            "Article Test Content",
            "Article 2 Content",
        ]

        expected_result = [
            {
                "source": "Zambia National Broadcasting Corporation (ZNBC)",
                "url": "https://www.znbc.co.zm/news/article2",
                "title": "Article 2",
                "content": "Article 2 Content",
                "category": "",
            },
            {
                "source": "Zambia National Broadcasting Corporation (ZNBC)",
                "url": "https://www.znbc.co.zm/news/article-test",
                "title": "Article Test",
                "content": "Article Test Content",
                "category": "",
            },
        ]

        result = get_news()

        self.assertEqual(result, expected_result)
        mock_requests.get.assert_called_once_with(
            "https://www.znbc.co.zm/news/",
            headers={"User-Agent": "Mock User Agent"},
            timeout=60,
        )
        mock_get_article_detail.assert_has_calls(
            [
                call("https://www.znbc.co.zm/news/article-test"),
                call("https://www.znbc.co.zm/news/article2"),
            ]
        )

    @patch("app.core.news.znbc.requests")
    @patch("app.core.news.znbc.ua")
    def test_get_news_no_articles(self, mock_user_agent, mock_requests):
        mock_user_agent.random = "Mock User Agent"
        self.mock_response.text = "<html></html>"
        mock_requests.get.return_value = self.mock_response

        expected_result = []

        result = get_news()

        self.assertEqual(result, expected_result)
        mock_requests.get.assert_called_once_with(
            "https://www.znbc.co.zm/news/",
            headers={"User-Agent": "Mock User Agent"},
            timeout=60,
        )


if __name__ == "__main__":
    unittest.main()
