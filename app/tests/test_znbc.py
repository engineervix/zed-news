import unittest
from unittest.mock import MagicMock, patch

from app.core.news.znbc import get_article_detail, get_news
from app.core.utilities import today_human_readable, today_iso_fmt


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

    @patch("app.core.news.znbc.requests")
    def test_get_article_detail_none(self, mock_requests):
        """
        We expect an article to have a div with class entry-content.
        If this is not found, we raise an AttributeError & return None
        """
        mock_response = MagicMock()
        mock_response.text = """
            <article>
                <div>
                    <p>Paragraph 1</p>
                    <p>Paragraph 2</p>
                </div>
            </article>
        """
        mock_requests.get.return_value = mock_response

        expected_content = None
        result = get_article_detail(self.url)
        self.assertEqual(result, expected_content)

        mock_requests.get.assert_called_once_with(self.url)


class TestGetNews(unittest.TestCase):
    @patch("app.core.news.znbc.get_article_detail")
    @patch("app.core.news.znbc.requests.get")
    def test_get_news(self, mock_get, mock_get_article_detail):
        mock_response = MagicMock()
        mock_response.text = f"""
            <html>
                <body>
                    <main id="main-content">
                        <article class="single-page-content global-single-content">
                            <div class="entry-content">
                                <article>
                                    <h3 class="entry-title"><a href="https://www.znbc.co.zm/news/123">News Title 1</a></h3>
                                    <time class="entry-date" datetime="{today_iso_fmt}">{today_human_readable}</time>
                                    Posted in <a href="/category-1" class="category-item">Category 1</a>
                                </article>
                                <article>
                                    <h3 class="entry-title"><a href="https://www.znbc.co.zm/news/456">News Title 2</a></h3>
                                    <time class="entry-date" datetime="2023-06-17">June 17, 2023</time>
                                    Posted in <a href="/category-2" class="category-item">Category 2</a>
                                </article>
                            </div>
                        </article>
                    </main>
                </body>
            </html>
        """

        mock_get.return_value = mock_response
        mock_get_article_detail.return_value = "News Content 1"

        result = get_news()

        expected_result = [
            {
                "source": "Zambia National Broadcasting Corporation (ZNBC)",
                "url": "https://www.znbc.co.zm/news/123",
                "title": "News Title 1",
                "content": "News Content 1",
                "category": "Category 1",
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
                        <article class="single-page-content global-single-content">
                            <div class="entry-content">
                                Stuff
                            </div>
                        </article>
                    </main>
                </body>
            </html>
        """

        mock_get.return_value = mock_response

        result = get_news()

        expected_result = []
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
