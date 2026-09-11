import unittest
from datetime import date
from unittest.mock import MagicMock, patch

from app.core.summarization.corroboration import exa_search


class TestExaSearch(unittest.TestCase):
    @patch("app.core.summarization.corroboration.EXA_API_KEY", "test-key")
    @patch("app.core.summarization.corroboration.requests")
    def test_exa_search(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [{"title": "A fuel hike story", "url": "https://x.zm/a"}]}
        mock_requests.post.return_value = mock_response

        results = exa_search("fuel price hike", date(2026, 1, 1), date(2026, 9, 11))

        self.assertEqual(results, [{"title": "A fuel hike story", "url": "https://x.zm/a"}])
        mock_response.raise_for_status.assert_called_once()

        _, kwargs = mock_requests.post.call_args
        self.assertEqual(kwargs["headers"]["x-api-key"], "test-key")
        self.assertEqual(
            kwargs["json"],
            {
                "query": "fuel price hike",
                "numResults": 1,
                "category": "news",
                "startPublishedDate": "2026-01-01",
                "endPublishedDate": "2026-09-11",
            },
        )

    @patch("app.core.summarization.corroboration.EXA_API_KEY", "test-key")
    @patch("app.core.summarization.corroboration.requests")
    def test_exa_search_passes_through_custom_num_results(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_requests.post.return_value = mock_response

        exa_search("topic", date(2026, 1, 1), date(2026, 1, 2), num_results=10)

        _, kwargs = mock_requests.post.call_args
        self.assertEqual(kwargs["json"]["numResults"], 10)

    @patch("app.core.summarization.corroboration.EXA_API_KEY", None)
    @patch("app.core.summarization.corroboration.requests")
    def test_exa_search_returns_empty_without_a_configured_key(self, mock_requests):
        # Informational metric only - a missing key shouldn't crash an eval
        # run, just skip corroboration.
        results = exa_search("topic", date(2026, 1, 1), date(2026, 1, 2))

        self.assertEqual(results, [])
        mock_requests.post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
