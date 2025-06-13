import shutil
import tempfile
import unittest
from unittest.mock import patch

from app.core import run


class TestRun(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.patcher_data_dir = patch("app.core.run.DATA_DIR", self.temp_dir)
        self.mock_data_dir = self.patcher_data_dir.start()

    def tearDown(self):
        self.patcher_data_dir.stop()
        shutil.rmtree(self.temp_dir)

    @patch("app.core.run.close_database")
    @patch("app.core.run.render_jinja_template")
    @patch("app.core.run.subprocess.run")
    @patch("app.core.run.create_news_digest")
    @patch("app.core.run.save_news_to_db")
    @patch("app.core.run.initialize_database")
    @patch("app.core.run.save_news_to_file")
    @patch("app.core.run.get_latest_news")
    @patch("app.core.run.configure_logging")
    @patch("app.core.run.load_dotenv")
    @patch("app.core.run.init")
    def test_main_workflow(
        self,
        mock_init,
        mock_dotenv,
        mock_logging,
        mock_get_news,
        mock_save_file,
        mock_init_db,
        mock_save_db,
        mock_create_digest,
        mock_subprocess,
        mock_render,
        mock_close_db,
    ):
        # Mock return values
        mock_get_news.return_value = [{"title": "Test News"}]
        mock_create_digest.return_value = {"content": "Test Digest"}

        # Run the main function
        run.main()

        # Assert that all functions are called
        mock_init.assert_called_once()
        mock_dotenv.assert_called_once()
        mock_logging.assert_called_once()
        mock_get_news.assert_called_once()
        mock_save_file.assert_called_once()
        mock_init_db.assert_called_once()
        mock_save_db.assert_called_once()
        mock_create_digest.assert_called_once()

        # Assert subprocess calls for moving files
        self.assertEqual(mock_subprocess.call_count, 4)

        mock_render.assert_called_once()
        mock_close_db.assert_called_once()


if __name__ == "__main__":
    unittest.main()
