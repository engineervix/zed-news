import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, mock_open, patch

from app.core.news.digest import create_news_digest, update_article_with_summary
from app.core.utilities import today


class TestDigest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.patcher_data_dir = patch("app.core.news.digest.DATA_DIR", self.temp_dir)
        self.mock_data_dir = self.patcher_data_dir.start()

    def tearDown(self):
        self.patcher_data_dir.stop()
        shutil.rmtree(self.temp_dir)

    @patch("app.core.news.digest.Article")
    def test_update_article_with_summary_found(self, mock_article_class):
        mock_article_instance = MagicMock()
        mock_article_class.select.return_value.where.return_value.first.return_value = mock_article_instance
        title = "Test Title"
        url = "http://example.com"
        date = today
        summary = "Test summary."

        update_article_with_summary(title, url, date, summary)

        mock_article_class.select.return_value.where.assert_called_once()
        mock_article_instance.save.assert_called_once()
        self.assertEqual(mock_article_instance.summary, summary)

    @patch("app.core.news.digest.logger")
    @patch("app.core.news.digest.Article")
    def test_update_article_with_summary_not_found(self, mock_article_class, mock_logger):
        mock_article_class.select.return_value.where.return_value.first.return_value = None
        title = "Test Title"
        url = "http://example.com"
        date = today
        summary = "Test summary."

        update_article_with_summary(title, url, date, summary)

        mock_article_class.select.return_value.where.assert_called_once()
        mock_logger.warning.assert_called_with(
            f"Could not find article with title '{title}', URL '{url}', and date '{date}'"
        )

    @patch("sys.exit")
    @patch("app.core.news.digest.update_article_with_summary")
    @patch("app.core.news.digest.brief_summary")
    @patch("builtins.open", new_callable=mock_open)
    @patch("app.core.news.digest.OpenAI")
    @patch("app.core.news.digest.logger")
    def test_create_news_digest_success(
        self, mock_logger, mock_openai, mock_open_file, mock_brief_summary, mock_update_article, mock_exit
    ):
        news = [
            {
                "source": "ZNBC",
                "url": "http://znbc.co.zm/news/1",
                "title": "Title 1",
                "content": "Content 1",
                "category": "National",
            },
            {
                "source": "Mwebantu",
                "url": "http://mwebantu.com/news/1",
                "title": "Title 2",
                "content": "Content 2",
                "category": "Local",
            },
        ]
        dest = os.path.join(self.temp_dir, "digest.md")
        summarizer = MagicMock(return_value="Summary.")

        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "Generated Digest"
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        result = create_news_digest(news, dest, summarizer)

        self.assertEqual(summarizer.call_count, 2)
        mock_update_article.assert_called()
        self.assertEqual(mock_update_article.call_count, 2)
        mock_openai.return_value.chat.completions.create.assert_called_once()
        mock_logger.info.assert_any_call(f"News digest created successfully: {dest}")
        self.assertIsNotNone(result)
        self.assertEqual(result["total_articles"], 2)
        self.assertEqual(result["content"], "Generated Digest")

    @patch("app.core.news.digest.update_article_with_summary")
    @patch("app.core.news.digest.brief_summary")
    @patch("builtins.open", new_callable=mock_open)
    @patch("app.core.news.digest.OpenAI")
    def test_create_news_digest_uses_brief_summary(
        self, mock_openai, mock_open_file, mock_brief_summary, mock_update_article
    ):
        news = [{"source": "ZNBC", "url": "url", "title": f"Title {i}", "content": "content"} for i in range(40)]
        dest = os.path.join(self.temp_dir, "digest.md")
        summarizer = MagicMock(return_value="Summary.")
        mock_brief_summary.return_value = "Brief Summary."

        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "Generated Digest"
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        create_news_digest(news, dest, summarizer)

        self.assertEqual(summarizer.call_count, 0)
        self.assertEqual(mock_brief_summary.call_count, 40)

    @patch("sys.exit")
    @patch("builtins.open", new_callable=mock_open)
    @patch("app.core.news.digest.OpenAI")
    @patch("app.core.news.digest.logger")
    def test_create_news_digest_empty_digest(self, mock_logger, mock_openai, mock_open_file, mock_sys_exit):
        news = [{"source": "ZNBC", "url": "url", "title": "Title 1", "content": "Content 1"}]
        dest = os.path.join(self.temp_dir, "digest.md")
        summarizer = MagicMock(return_value="Summary.")

        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = ""  # Empty digest
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        with patch("app.core.news.digest.update_article_with_summary"):
            create_news_digest(news, dest, summarizer)

        mock_logger.error.assert_called_with("Generated digest is empty")
        mock_sys_exit.assert_called_with(1)
