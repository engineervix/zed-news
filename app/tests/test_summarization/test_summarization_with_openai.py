import unittest
from unittest.mock import patch

from app.core.summarization.backends.openai import summarize


class TestOpenAIBackend(unittest.TestCase):
    """Test cases for OpenAI backend summarization"""

    def setUp(self):
        self.content = "This is a test article content that needs to be summarized."
        self.title = "Test Article"
        self.mock_summary = "A brief summary of the test article."

    @patch("app.core.summarization.backends.openai.logging")
    @patch("app.core.summarization.backends.openai.llm")
    def test_summarize_successful(self, mock_llm, mock_logging):
        # Set up mock token count to ensure positive width for textwrap
        mock_llm.get_num_tokens.return_value = 100

        # Set up mock response
        mock_llm.return_value = self.mock_summary

        # Call the function
        result = summarize(self.content, self.title)

        # Verify logging was called with token count
        mock_logging.info.assert_called_once_with(
            f"'{self.title}' and its prompt has {mock_llm.get_num_tokens.return_value} tokens"
        )

        # Verify the result
        self.assertEqual(result, self.mock_summary)

    @patch("app.core.summarization.backends.openai.logging")
    @patch("app.core.summarization.backends.openai.llm")
    def test_summarize_with_long_content(self, mock_llm, mock_logging):
        # Create long content that exceeds token limit
        long_content = "Very long content " * 1000

        # Set up mock responses
        mock_llm.get_num_tokens.side_effect = [4000, 100]  # First for template, then for truncated content
        mock_llm.return_value = self.mock_summary

        # Call the function
        result = summarize(long_content, self.title)

        # Verify the result
        self.assertEqual(result, self.mock_summary)

        # Verify token counting was called
        self.assertEqual(mock_llm.get_num_tokens.call_count, 2)

    @patch("app.core.summarization.backends.openai.logging")
    @patch("app.core.summarization.backends.openai.llm")
    def test_summarize_with_empty_content(self, mock_llm, mock_logging):
        # Set up mock response for empty content
        mock_llm.get_num_tokens.return_value = 50
        mock_llm.return_value = ""

        # Call the function with empty content
        result = summarize("", self.title)

        # Verify empty summary is returned
        self.assertEqual(result, "")

    @patch("app.core.summarization.backends.openai.logging")
    @patch("app.core.summarization.backends.openai.llm")
    def test_summarize_with_api_error(self, mock_llm, mock_logging):
        # Set up mock token count to ensure positive width for textwrap
        mock_llm.get_num_tokens.return_value = 100

        # Make the API call raise an exception
        mock_llm.side_effect = Exception("API Error")

        # Call the function and verify it raises the exception
        with self.assertRaises(Exception) as context:
            summarize(self.content, self.title)

        # Verify the error message
        self.assertEqual(str(context.exception), "API Error")

    @patch("app.core.summarization.backends.openai.logging")
    @patch("app.core.summarization.backends.openai.llm")
    def test_token_counting(self, mock_llm, mock_logging):
        # Set up mock responses for different token counts
        mock_llm.get_num_tokens.side_effect = [200, 150]  # First for template, then for complete prompt
        mock_llm.return_value = self.mock_summary

        # Call the function
        result = summarize(self.content, self.title)

        # Verify token counting was called twice
        self.assertEqual(mock_llm.get_num_tokens.call_count, 2)

        # Verify the result
        self.assertEqual(result, self.mock_summary)


if __name__ == "__main__":
    unittest.main()
