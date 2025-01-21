import unittest
from unittest.mock import MagicMock, patch

from cohere.error import CohereAPIError

from app.core.summarization.backends.cohere import summarize


class TestCohere(unittest.TestCase):
    def setUp(self):
        # Create content that meets Cohere's minimum length requirement (250 chars)
        self.content = "This is a test article content that needs to be summarized. " * 10
        self.title = "Test Article"
        self.mock_summary = "This is a summarized version of the test article."

    @patch("app.core.summarization.backends.cohere.logging")
    @patch("app.core.summarization.backends.cohere.co")
    def test_summarize_successful(self, mock_co, mock_logging):
        # Set up mock response
        mock_response = MagicMock()
        mock_response.summary = self.mock_summary
        mock_co.summarize.return_value = mock_response

        # Call the function
        result = summarize(self.content, self.title)

        # Verify the function was called with correct parameters
        mock_co.summarize.assert_called_once_with(
            text=self.content,
            model="summarize-xlarge",
            temperature=0,
            length="auto",
            format="paragraph",
            extractiveness="auto",
            additional_command="in a manner suitable for reading as part of a podcast",
        )

        # Verify logging was called
        mock_logging.info.assert_called_once_with(f"Summarizing '{self.title}' via Cohere ...")

        # Verify the result
        self.assertEqual(result, self.mock_summary)

    @patch("app.core.summarization.backends.cohere.logging")
    @patch("app.core.summarization.backends.cohere.co")
    def test_summarize_with_empty_content(self, mock_co, mock_logging):
        # Make the API call raise an exception for empty content
        mock_co.summarize.side_effect = CohereAPIError("invalid request: required 'text' param is missing or empty.")

        # Call the function with empty content and verify it raises the exception
        with self.assertRaises(CohereAPIError) as context:
            summarize("", self.title)

        # Verify the error message
        self.assertEqual(str(context.exception), "invalid request: required 'text' param is missing or empty.")

        # Verify logging was still called
        mock_logging.info.assert_called_once_with(f"Summarizing '{self.title}' via Cohere ...")

    @patch("app.core.summarization.backends.cohere.logging")
    @patch("app.core.summarization.backends.cohere.co")
    def test_summarize_with_short_content(self, mock_co, mock_logging):
        # Make the API call raise an exception for short content
        mock_co.summarize.side_effect = CohereAPIError("invalid request: text must be longer than 250 characters")

        # Call the function with short content and verify it raises the exception
        with self.assertRaises(CohereAPIError) as context:
            summarize("This is too short", self.title)

        # Verify the error message
        self.assertEqual(str(context.exception), "invalid request: text must be longer than 250 characters")

    @patch("app.core.summarization.backends.cohere.logging")
    @patch("app.core.summarization.backends.cohere.co")
    def test_summarize_with_api_error(self, mock_co, mock_logging):
        # Make the API call raise a generic exception
        mock_co.summarize.side_effect = CohereAPIError("API Error")

        # Call the function and verify it raises the exception
        with self.assertRaises(CohereAPIError) as context:
            summarize(self.content, self.title)

        # Verify the error message
        self.assertEqual(str(context.exception), "API Error")


if __name__ == "__main__":
    unittest.main()
