import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

import dspy
from dspy.utils.dummies import DummyLM

from app.core.news.digest import create_news_digest, fix_markdown_headings


class TestDigest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.patcher_data_dir = patch("app.core.news.digest.DATA_DIR", self.temp_dir)
        self.mock_data_dir = self.patcher_data_dir.start()

        # Force the raw module path regardless of whether this machine has a
        # locally-generated compiled program - keeps tests deterministic.
        self.patcher_compiled_program = patch(
            "app.core.summarization.backends.dspy_backend.COMPILED_PROGRAM_PATH",
            Path(self.temp_dir) / "no_compiled_program_here.json",
        )
        self.patcher_compiled_program.start()

    def tearDown(self):
        self.patcher_compiled_program.stop()
        self.patcher_data_dir.stop()
        shutil.rmtree(self.temp_dir)

    @patch("sys.exit")
    @patch("builtins.open", new_callable=mock_open)
    @patch("app.core.news.digest.logger")
    def test_create_news_digest_success(self, mock_logger, mock_open_file, mock_exit):
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

        with dspy.context(lm=DummyLM([{"digest": "Generated Digest"}])):
            result = create_news_digest(news, dest)

        mock_logger.info.assert_any_call(f"News digest created successfully: {dest}")
        self.assertIsNotNone(result)
        self.assertEqual(result["total_articles"], 2)
        self.assertEqual(result["content"], "Generated Digest")
        # Check that summary is not in the articles
        self.assertNotIn("summary", result["articles"][0])

    @patch("sys.exit")
    @patch("builtins.open", new_callable=mock_open)
    @patch("app.core.news.digest.logger")
    def test_create_news_digest_empty_generation(self, mock_logger, mock_open_file, mock_exit):
        news = [
            {"source": "ZNBC", "title": "Title 1", "content": "Content 1", "url": "url1"},
        ]
        dest = os.path.join(self.temp_dir, "digest.md")

        with dspy.context(lm=DummyLM([{"digest": ""}])):
            create_news_digest(news, dest)

        mock_exit.assert_called_once_with(1)
        mock_logger.error.assert_called_with("Generated digest is empty")

    @patch("app.core.news.digest.logger")
    def test_create_news_digest_no_news(self, mock_logger):
        news = []
        dest = os.path.join(self.temp_dir, "digest.md")

        result = create_news_digest(news, dest)

        self.assertIsNone(result)
        mock_logger.info.assert_called_with("No news to create digest from.")

    def test_fix_markdown_headings_no_space(self):
        text = "##Heading with no space"
        expected = "## Heading with no space"
        result = fix_markdown_headings(text)
        self.assertEqual(result, expected)

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
    @patch("builtins.open", new_callable=mock_open)
    @patch("app.core.news.digest.logger")
    def test_create_news_digest_with_markdown_fix(self, mock_logger, mock_open_file, mock_exit):
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

        # Generate content with improperly formatted headings
        generated = "##Main Stories\nSome content\n###Brief Updates\nMore content"
        with dspy.context(lm=DummyLM([{"digest": generated}])):
            result = create_news_digest(news, dest)

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
