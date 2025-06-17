import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from app.core.news.eleventify import create_digest_description, get_digest_metadata, render_jinja_template
from app.core.utilities import today_human_readable, today_iso_fmt


class TestEleventify(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.patcher_data_dir = patch("app.core.utilities.DATA_DIR", self.temp_dir)
        self.patcher_dist_file = patch("app.core.news.eleventify.dist_file", f"{self.temp_dir}/{today_iso_fmt}.njk")

        self.mock_data_dir = self.patcher_data_dir.start()
        self.mock_dist_file = self.patcher_dist_file.start()

        self.digest_metadata_file = os.path.join(self.mock_data_dir, f"{today_iso_fmt}/{today_iso_fmt}_digest.json")
        os.makedirs(os.path.dirname(self.digest_metadata_file), exist_ok=True)

    def tearDown(self):
        self.patcher_data_dir.stop()
        self.patcher_dist_file.stop()
        shutil.rmtree(self.temp_dir)

    @patch("app.core.news.eleventify.create_digest_description")
    @patch("app.core.news.eleventify.get_digest_metadata")
    @patch("app.core.news.eleventify.logger")
    def test_render_jinja_template(self, mock_logger, mock_get_digest_metadata, mock_create_digest_description):
        mock_get_digest_metadata.return_value = {
            "content": "This is the main digest content.",
            "sources": ["Source A", "Source B"],
            "articles": [
                {"source": "Source A", "url": "http://example.com/a", "title": "Article A"},
                {"source": "Source B", "url": "http://example.com/b", "title": "Article B"},
            ],
            "total_articles": 2,
            "generated_at": "2024-01-01T12:00:00Z",
        }
        mock_create_digest_description.return_value = "A fantastic news digest for you."

        render_jinja_template()

        dist_file_path = f"{self.temp_dir}/{today_iso_fmt}.njk"
        self.assertTrue(os.path.exists(dist_file_path))
        with open(dist_file_path, "r") as f:
            content = f.read()

        self.assertIn(f'title: "News Digest - {today_human_readable}"', content)
        self.assertIn('description: "A fantastic news digest for you."', content)
        self.assertIn("This is the main digest content.", content)
        self.assertIn("count: 2", content)
        self.assertIn("sources: 2", content)
        self.assertIn("Article A", content)
        mock_logger.info.assert_any_call("Rendering Jinja template for daily digest...")
        mock_logger.info.assert_any_call(f"Daily digest template rendered successfully: {dist_file_path}")

    def test_get_digest_metadata(self):
        mock_data = {"key": "value"}
        with open(self.digest_metadata_file, "w") as f:
            json.dump(mock_data, f)

        with patch("app.core.news.eleventify.digest_metadata_file", self.digest_metadata_file):
            data = get_digest_metadata()
            self.assertEqual(data, mock_data)

    def test_get_digest_metadata_file_not_found(self):
        with patch("app.core.news.eleventify.logger") as mock_logger:
            with patch("app.core.news.eleventify.digest_metadata_file", "non_existent_file.json"):
                data = get_digest_metadata()
                self.assertEqual(data, {})
                mock_logger.error.assert_called_with("Digest metadata file not found: non_existent_file.json")

    @patch("app.core.news.eleventify.gemini_client")
    def test_create_digest_description_success(self, mock_gemini_client):
        mock_response = MagicMock()
        mock_response.text = "This is a generated description."
        mock_gemini_client.models.generate_content.return_value = mock_response

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
            description = create_digest_description("content", "date")
            self.assertIn("This is a generated description.", description)


if __name__ == "__main__":
    unittest.main()
