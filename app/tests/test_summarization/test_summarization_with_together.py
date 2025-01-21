import unittest
from unittest.mock import MagicMock, patch

from together import error

from app.core.summarization.backends.together import brief_summary, summarize


class TestTogether(unittest.TestCase):
    def setUp(self):
        self.content = "This is a test article content that needs to be summarized."
        self.title = "Test Article"
        self.mock_summary = "A brief summary of the test article."

    @patch("app.core.summarization.backends.together.time.sleep")
    @patch("app.core.summarization.backends.together.logging")
    @patch("app.core.summarization.backends.together.client")
    def test_summarize_successful(self, mock_client, mock_logging, mock_sleep):
        # Set up mock response
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = self.mock_summary
        mock_client.chat.completions.create.return_value = mock_completion

        # Call the function
        result = summarize(self.content, self.title)

        # Verify result and logging
        self.assertEqual(result, self.mock_summary)
        mock_logging.info.assert_called_with(mock_completion)

    @patch("app.core.summarization.backends.together.time.sleep")
    @patch("app.core.summarization.backends.together.logging")
    @patch("app.core.summarization.backends.together.client")
    def test_summarize_with_service_error(self, mock_client, mock_logging, mock_sleep):
        # Set up mock to raise error and then succeed
        mock_client.chat.completions.create.side_effect = [
            error.ServiceUnavailableError(),
            MagicMock(choices=[MagicMock(message=MagicMock(content=self.mock_summary))]),
        ]

        # Call the function
        result = summarize(self.content, self.title)

        # Verify retry behavior
        self.assertEqual(result, self.mock_summary)
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        # Check that sleep was called twice with correct values in correct order
        mock_sleep.assert_has_calls(
            [
                unittest.mock.call(10),  # First sleep during retry
                unittest.mock.call(1.5),  # Second sleep after successful call
            ]
        )

    @patch("app.core.summarization.backends.together.time.sleep")
    @patch("app.core.summarization.backends.together.logging")
    @patch("app.core.summarization.backends.together.client")
    @patch("app.core.summarization.backends.together.sys.exit")
    def test_summarize_max_retries(self, mock_exit, mock_client, mock_logging, mock_sleep):
        # Make all calls fail with service error
        mock_client.chat.completions.create.side_effect = error.ServiceUnavailableError()

        # Call the function
        summarize(self.content, self.title)

        # Verify error handling
        self.assertEqual(mock_client.chat.completions.create.call_count, 30)
        mock_logging.error.assert_called_with("Failed after 30 attempts.")
        mock_exit.assert_called_once_with(1)

    @patch("app.core.summarization.backends.together.time.sleep")
    @patch("app.core.summarization.backends.together.logging")
    @patch("app.core.summarization.backends.together.client")
    def test_brief_summary_successful(self, mock_client, mock_logging, mock_sleep):
        # Set up mock response
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = self.mock_summary
        mock_client.chat.completions.create.return_value = mock_completion

        # Call the function
        result = brief_summary(self.content, self.title)

        # Verify result and logging
        self.assertEqual(result, self.mock_summary)
        mock_logging.info.assert_called_with(mock_completion)


if __name__ == "__main__":
    unittest.main()
