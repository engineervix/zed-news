import unittest
from unittest.mock import MagicMock, patch

from app.core.summarization.embeddings import _MAX_EMBEDDING_CHARS, embed_text, embed_texts


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

        # embed_text delegates to embed_texts, so even a single article goes
        # out as a one-item batch - OpenRouter's /v1/embeddings input is a list.
        _, kwargs = mock_requests.post.call_args
        self.assertEqual(kwargs["json"], {"model": "baai/bge-m3", "input": ["some article content"]})
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-key")

    @patch("app.core.summarization.embeddings.requests")
    def test_embed_text_returns_none_for_empty_content(self, mock_requests):
        # OpenRouter's /v1/embeddings rejects an empty-string input with a 400 -
        # confirmed against real data (an empty-content article crashed the backfill).
        self.assertIsNone(embed_text(""))
        self.assertIsNone(embed_text("   "))
        mock_requests.post.assert_not_called()

    @patch("app.core.summarization.embeddings.requests")
    def test_embed_text_truncates_content_over_the_token_cap(self, mock_requests):
        # bge-m3's real cap is 8192 tokens - a live 400 against a real 33k-char
        # article confirmed this, and that this model packs ~3.99 chars/token
        # with no margin. _MAX_EMBEDDING_CHARS uses a 3.5 chars/token estimate
        # for real headroom.
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [{"embedding": [0.1], "index": 0}]}
        mock_requests.post.return_value = mock_response

        long_content = "x" * (_MAX_EMBEDDING_CHARS + 1000)
        embed_text(long_content)

        _, kwargs = mock_requests.post.call_args
        sent_input = kwargs["json"]["input"][0]
        self.assertEqual(len(sent_input), _MAX_EMBEDDING_CHARS)
        self.assertEqual(sent_input, long_content[:_MAX_EMBEDDING_CHARS])


class TestEmbedTexts(unittest.TestCase):
    @patch("app.core.summarization.embeddings.OPENROUTER_API_KEY", "test-key")
    @patch("app.core.summarization.embeddings.requests")
    def test_embed_texts_batches_in_one_call(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"embedding": [0.1], "index": 0},
                {"embedding": [0.2], "index": 1},
                {"embedding": [0.3], "index": 2},
            ]
        }
        mock_requests.post.return_value = mock_response

        result = embed_texts(["first", "second", "third"])

        self.assertEqual(result, [[0.1], [0.2], [0.3]])
        mock_requests.post.assert_called_once()
        _, kwargs = mock_requests.post.call_args
        self.assertEqual(kwargs["json"], {"model": "baai/bge-m3", "input": ["first", "second", "third"]})

    @patch("app.core.summarization.embeddings.requests")
    def test_embed_texts_skips_empty_entries_and_keeps_their_position(self, mock_requests):
        mock_response = MagicMock()
        # Only "first" and "third" go to the API - "" and "   " are excluded.
        mock_response.json.return_value = {
            "data": [
                {"embedding": [0.1], "index": 0},
                {"embedding": [0.3], "index": 1},
            ]
        }
        mock_requests.post.return_value = mock_response

        result = embed_texts(["first", "", "third", "   "])

        self.assertEqual(result, [[0.1], None, [0.3], None])
        _, kwargs = mock_requests.post.call_args
        self.assertEqual(kwargs["json"]["input"], ["first", "third"])

    @patch("app.core.summarization.embeddings.requests")
    def test_embed_texts_returns_all_none_without_calling_api_when_all_empty(self, mock_requests):
        result = embed_texts(["", "   ", ""])

        self.assertEqual(result, [None, None, None])
        mock_requests.post.assert_not_called()

    @patch("app.core.summarization.embeddings.requests")
    def test_embed_texts_maps_out_of_order_response_index_back_to_position(self, mock_requests):
        # OpenRouter's own docs don't guarantee response.data ordering matches
        # request order - assembling by each item's own "index" field, not
        # list position, is what makes this safe either way.
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"embedding": [0.2], "index": 1},
                {"embedding": [0.1], "index": 0},
            ]
        }
        mock_requests.post.return_value = mock_response

        result = embed_texts(["first", "second"])

        self.assertEqual(result, [[0.1], [0.2]])
