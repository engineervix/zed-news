import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, mock_open, patch

from app.core.news.digest import (
    create_news_digest,
    fix_markdown_headings,
    remove_title_headings,
    update_article_with_summary,
)
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
    @patch("app.core.news.digest.client")
    @patch("app.core.news.digest.logger")
    def test_create_news_digest_success(
        self, mock_logger, mock_client, mock_open_file, mock_brief_summary, mock_update_article, mock_exit
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
        mock_client.chat.completions.create.return_value = mock_completion

        result = create_news_digest(news, dest, summarizer)

        self.assertEqual(summarizer.call_count, 2)
        mock_update_article.assert_called()
        self.assertEqual(mock_update_article.call_count, 2)
        mock_client.chat.completions.create.assert_called_once()
        mock_logger.info.assert_any_call(f"News digest created successfully: {dest}")
        self.assertIsNotNone(result)
        self.assertEqual(result["total_articles"], 2)
        self.assertEqual(result["content"], "Generated Digest")

    @patch("app.core.news.digest.update_article_with_summary")
    @patch("app.core.news.digest.brief_summary")
    @patch("builtins.open", new_callable=mock_open)
    @patch("app.core.news.digest.client")
    def test_create_news_digest_uses_brief_summary(
        self, mock_client, mock_open_file, mock_brief_summary, mock_update_article
    ):
        news = [{"source": "ZNBC", "url": "url", "title": f"Title {i}", "content": "content"} for i in range(40)]
        dest = os.path.join(self.temp_dir, "digest.md")
        summarizer = MagicMock(return_value="Summary.")
        mock_brief_summary.return_value = "Brief Summary."

        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "Generated Digest"
        mock_client.chat.completions.create.return_value = mock_completion

        create_news_digest(news, dest, summarizer)

        self.assertEqual(summarizer.call_count, 0)
        self.assertEqual(mock_brief_summary.call_count, 40)

    @patch("sys.exit")
    @patch("builtins.open", new_callable=mock_open)
    @patch("app.core.news.digest.client")
    @patch("app.core.news.digest.logger")
    def test_create_news_digest_empty_digest(self, mock_logger, mock_client, mock_open_file, mock_sys_exit):
        news = [{"source": "ZNBC", "url": "url", "title": "Title 1", "content": "Content 1"}]
        dest = os.path.join(self.temp_dir, "digest.md")
        summarizer = MagicMock(return_value="Summary.")

        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = ""  # Empty digest
        mock_client.chat.completions.create.return_value = mock_completion

        with patch("app.core.news.digest.update_article_with_summary"):
            create_news_digest(news, dest, summarizer)

        mock_logger.error.assert_called_with("Generated digest is empty")
        mock_sys_exit.assert_called_with(1)

    def test_markdown_heading_fix(self):
        """Test that markdown headings without spaces are properly fixed"""

        test_cases = [
            # Basic headings missing spaces
            {
                "input": "##Main Stories\nSome content here\n###Subsection\nMore content",
                "expected": "## Main Stories\nSome content here\n### Subsection\nMore content",
                "description": "Basic headings missing spaces",
            },
            # Already correct headings
            {
                "input": "## Main Stories\nSome content here\n### Subsection\nMore content",
                "expected": "## Main Stories\nSome content here\n### Subsection\nMore content",
                "description": "Already correct headings",
            },
            # Mixed scenarios
            {
                "input": "##Brief Updates\n## Closing Reflection\n###Another Section",
                "expected": "## Brief Updates\n## Closing Reflection\n### Another Section",
                "description": "Mixed correct and incorrect headings",
            },
            # All heading levels
            {
                "input": "#Title\n##Section\n###Subsection\n####Subsubsection\n#####Five\n######Six",
                "expected": "# Title\n## Section\n### Subsection\n#### Subsubsection\n##### Five\n###### Six",
                "description": "All heading levels",
            },
            # Should not affect non-headings
            {
                "input": "This is ##not a heading because it's not at start of line\n##This is a heading",
                "expected": "This is ##not a heading because it's not at start of line\n## This is a heading",
                "description": "Only fix headings at start of line",
            },
            # Multiple hash sequences (should not be affected)
            {
                "input": "######## Too many hashes\n## Normal heading",
                "expected": "######## Too many hashes\n## Normal heading",
                "description": "Should not affect more than 6 hashes",
            },
        ]

        for test_case in test_cases:
            with self.subTest(description=test_case["description"]):
                result = fix_markdown_headings(test_case["input"])
                self.assertEqual(
                    result,
                    test_case["expected"],
                    f"Failed for case: {test_case['description']}\n"
                    f"Input: {repr(test_case['input'])}\n"
                    f"Expected: {repr(test_case['expected'])}\n"
                    f"Got: {repr(result)}",
                )

    @patch("sys.exit")
    @patch("app.core.news.digest.update_article_with_summary")
    @patch("app.core.news.digest.brief_summary")
    @patch("builtins.open", new_callable=mock_open)
    @patch("app.core.news.digest.client")
    @patch("app.core.news.digest.logger")
    def test_create_news_digest_with_markdown_fix(
        self, mock_logger, mock_client, mock_open_file, mock_brief_summary, mock_update_article, mock_exit
    ):
        """Test that create_news_digest properly fixes markdown headings in the generated content"""
        news = [
            {
                "source": "ZNBC",
                "url": "http://znbc.co.zm/news/1",
                "title": "Title 1",
                "content": "Content 1",
                "category": "National",
            }
        ]
        dest = os.path.join(self.temp_dir, "digest.md")
        summarizer = MagicMock(return_value="Summary.")

        # Mock Together AI to return content with improperly formatted headings
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "##Main Stories\nSome content\n###Brief Updates\nMore content"
        mock_client.chat.completions.create.return_value = mock_completion

        result = create_news_digest(news, dest, summarizer)

        # Check that the markdown headings were fixed in the result
        expected_content = "## Main Stories\nSome content\n### Brief Updates\nMore content"
        self.assertEqual(result["content"], expected_content)

        # Verify the digest file was written with the corrected content
        # The mock_open_file is called twice: once for headlines, once for digest
        # We want to check the second call (digest file)
        write_calls = mock_open_file().write.call_args_list
        if len(write_calls) > 0:
            # The last write should be the digest content
            last_write_content = write_calls[-1][0][0]
            self.assertEqual(last_write_content, expected_content)

    def test_title_heading_removal(self):
        """Test that entire title-level heading lines (single #) are removed"""

        test_cases = [
            {
                "input": "# Main Title\n## Section\nSome text with # symbol\nIssue # 123",
                "expected": "## Section\nSome text with # symbol\nIssue # 123",
                "description": "Remove entire title heading line but preserve other content",
            },
            {
                "input": "## Section Only\nNo title here",
                "expected": "## Section Only\nNo title here",
                "description": "No title to remove",
            },
            {
                "input": "# Title\n# Another Title\n## Section",
                "expected": "## Section",
                "description": "Multiple title heading lines removed",
            },
            {
                "input": "Regular text\n# Title in middle\nMore text",
                "expected": "Regular text\nMore text",
                "description": "Title heading line in middle of content removed",
            },
            {
                "input": "# Title without newline",
                "expected": "",
                "description": "Title heading without trailing newline removed",
            },
        ]

        for test_case in test_cases:
            with self.subTest(description=test_case["description"]):
                # Use the helper function from digest.py
                result = remove_title_headings(test_case["input"])
                self.assertEqual(
                    result,
                    test_case["expected"],
                    f"Failed for case: {test_case['description']}\n"
                    f"Input: {repr(test_case['input'])}\n"
                    f"Expected: {repr(test_case['expected'])}\n"
                    f"Got: {repr(result)}",
                )
