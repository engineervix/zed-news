import unittest
from unittest.mock import MagicMock, patch

from app.core.news.znbc import get_article_detail


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


if __name__ == "__main__":
    unittest.main()
