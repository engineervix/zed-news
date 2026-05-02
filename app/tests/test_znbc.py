import unittest
from unittest.mock import MagicMock, patch

from app.core.news.znbc import get_article_detail, get_news
from app.core.utilities import today_human_readable


class TestGetArticleDetail(unittest.TestCase):
    def setUp(self):
        self.url = "https://example.com/article"

    @patch("app.core.news.znbc.requests")
    def test_get_article_detail(self, mock_requests):
        mock_response = MagicMock()
        mock_response.text = """
            <div class="elementor-widget-theme-post-content">
                <p>Paragraph 1</p>
                <p>Paragraph 2</p>
            </div>
        """
        mock_requests.get.return_value = mock_response

        expected_content = "Paragraph 1\nParagraph 2"
        result = get_article_detail(self.url)

        self.assertEqual(result, expected_content)
        mock_requests.get.assert_called_once_with(self.url, verify=False)

    @patch("app.core.news.znbc.requests")
    def test_get_article_detail_with_post_views(self, mock_requests):
        mock_response = MagicMock()
        mock_response.text = """
            <div class="elementor-widget-theme-post-content">
                <p>Paragraph 1</p>
                <p>Paragraph 2</p>
                <p>Post Views: 100</p>
            </div>
        """
        mock_requests.get.return_value = mock_response

        result = get_article_detail(self.url)
        self.assertEqual(result, "Paragraph 1\nParagraph 2")
        mock_requests.get.assert_called_once_with(self.url, verify=False)

    @patch("app.core.news.znbc.requests")
    def test_get_article_detail_none(self, mock_requests):
        """
        If elementor-widget-theme-post-content is not found, return None.
        """
        mock_response = MagicMock()
        mock_response.text = """
            <div class="some-other-div">
                <p>Paragraph 1</p>
            </div>
        """
        mock_requests.get.return_value = mock_response

        result = get_article_detail(self.url)
        self.assertIsNone(result)
        mock_requests.get.assert_called_once_with(self.url, verify=False)


class TestGetNews(unittest.TestCase):
    @patch("app.core.news.znbc.get_article_detail")
    @patch("app.core.news.znbc.requests.get")
    def test_get_news(self, mock_get, mock_get_article_detail):
        mock_response = MagicMock()
        mock_response.text = f"""
            <html>
                <body>
                    <article class="elementor-post">
                        <h3 class="elementor-post__title">
                            <a href="https://znbc.co.zm/?p=123">News Title 1</a>
                        </h3>
                        <span class="elementor-post-date">{today_human_readable}</span>
                    </article>
                    <article class="elementor-post">
                        <h3 class="elementor-post__title">
                            <a href="https://znbc.co.zm/?p=456">News Title 2</a>
                        </h3>
                        <span class="elementor-post-date">January 1, 2020</span>
                    </article>
                </body>
            </html>
        """

        mock_get.return_value = mock_response
        mock_get_article_detail.return_value = "News Content 1"

        result = get_news()

        expected_result = [
            {
                "source": "Zambia National Broadcasting Corporation (ZNBC)",
                "url": "https://znbc.co.zm/?p=123",
                "title": "News Title 1",
                "content": "News Content 1",
                "category": "",
            }
        ]
        self.assertEqual(result, expected_result)

    @patch("app.core.news.znbc.requests.get")
    def test_get_news_no_articles(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = """
            <html>
                <body>
                    <main id="main-content">
                        <div>No articles here</div>
                    </main>
                </body>
            </html>
        """

        mock_get.return_value = mock_response

        result = get_news()
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
