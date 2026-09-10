import unittest
from unittest.mock import MagicMock, patch

from app.core.summarization.embeddings import embed_text


class TestEmbedText(unittest.TestCase):
    @patch("app.core.summarization.embeddings.OPENROUTER_API_KEY", "test-key")
    @patch("app.core.summarization.embeddings.requests")
    def test_embed_text(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [{"embedding": [0.1, 0.2, 0.3], "index": 0}]}
        mock_requests.post.return_value = mock_response

        result = embed_text("some article content")

        self.assertEqual(result, [0.1, 0.2, 0.3])
        mock_response.raise_for_status.assert_called_once()

        _, kwargs = mock_requests.post.call_args
        self.assertEqual(kwargs["json"], {"model": "baai/bge-m3", "input": "some article content"})
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-key")

    @patch("app.core.summarization.embeddings.requests")
    def test_embed_text_returns_none_for_empty_content(self, mock_requests):
        # OpenRouter's /v1/embeddings rejects an empty-string input with a 400 -
        # confirmed against real data (an empty-content article crashed the backfill).
        self.assertIsNone(embed_text(""))
        self.assertIsNone(embed_text("   "))
        mock_requests.post.assert_not_called()
