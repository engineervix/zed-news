import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

from dspy.utils.dummies import DummyLM

from app.core.social import post
from app.core.utilities import today_iso_fmt


class TestSocialPost(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        post.DATA_DIR = self.temp_dir
        post.IMAGES_DIR = os.path.join(self.temp_dir, "promotional")
        os.makedirs(post.IMAGES_DIR, exist_ok=True)

        self.digest_dir = os.path.join(self.temp_dir, today_iso_fmt)
        os.makedirs(self.digest_dir, exist_ok=True)
        post.digest_file_path = os.path.join(self.digest_dir, f"{today_iso_fmt}_digest.json")

        # Force the raw module path regardless of whether this machine has
        # locally-generated compiled programs - keeps tests deterministic.
        no_program = Path(self.temp_dir) / "no_compiled_program_here.json"
        self.patcher_facebook_post_program = patch(
            "app.core.summarization.post.FACEBOOK_POST_COMPILED_PROGRAM_PATH", no_program
        )
        self.patcher_image_concept_program = patch(
            "app.core.summarization.post.IMAGE_CONCEPT_COMPILED_PROGRAM_PATH", no_program
        )
        self.patcher_facebook_post_program.start()
        self.patcher_image_concept_program.start()

    def tearDown(self):
        self.patcher_facebook_post_program.stop()
        self.patcher_image_concept_program.stop()
        shutil.rmtree(self.temp_dir)

    def test_get_digest_content_success(self):
        mock_data = {"content": "This is the digest content."}
        with open(post.digest_file_path, "w") as f:
            json.dump(mock_data, f)

        # The function reads the raw file, not just the JSON content key
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))) as mock_file:
            content = post.get_digest_content()
            self.assertEqual(content, json.dumps(mock_data))
            mock_file.assert_called_with(post.digest_file_path, "r")

    @patch("app.core.social.post.logger")
    def test_get_digest_content_not_found(self, mock_logger):
        content = post.get_digest_content()
        self.assertEqual(content, "")
        mock_logger.error.assert_called_with(f"Digest file not found at {post.digest_file_path}")

    @patch("app.core.social.post.FACEBOOK_POST_LM", DummyLM([{"post": "Generated Facebook Post"}]))
    def test_create_facebook_post_text_success(self):
        text = post.create_facebook_post_text("Some digest content.")
        self.assertEqual(text, "Generated Facebook Post")

    @patch("app.core.social.post.generate_facebook_post")
    @patch("app.core.social.post.logger")
    def test_create_facebook_post_text_failure(self, mock_logger, mock_generate):
        mock_generate.side_effect = Exception("API Error")
        text = post.create_facebook_post_text("Some digest content.")
        self.assertEqual(text, "")
        mock_logger.error.assert_called_with("Failed to generate Facebook post text: API Error")

    @patch("app.core.social.post.TOGETHER_API_KEY", "test_key")
    @patch("app.core.social.post.IMAGE_CONCEPT_LM", DummyLM([{"concept": "A generated image concept."}]))
    def test_get_image_prompt_concept_success(self):
        concept = post.get_image_prompt_concept("Some digest content.")
        self.assertEqual(concept, "A generated image concept.")

    @patch("app.core.social.post.TOGETHER_API_KEY", "test_key")
    @patch("app.core.social.post.generate_image_concept")
    @patch("app.core.social.post.logger")
    def test_get_image_prompt_concept_failure(self, mock_logger, mock_generate):
        mock_generate.side_effect = Exception("API Error")
        concept = post.get_image_prompt_concept("Some digest content.")
        self.assertEqual(concept, "")
        mock_logger.error.assert_called_with("Failed to generate image prompt concept: API Error")

    @patch("app.core.social.post.TOGETHER_API_KEY", "")
    @patch("app.core.social.post.logger")
    def test_get_image_prompt_concept_no_api_key(self, mock_logger):
        concept = post.get_image_prompt_concept("Some digest content.")
        self.assertEqual(concept, "")
        mock_logger.warning.assert_called_with("TOGETHER_API_KEY not set, skipping image prompt concept generation.")

    @patch("app.core.social.post.logger")
    def test_get_image_prompt_concept_no_content(self, mock_logger):
        concept = post.get_image_prompt_concept("")
        self.assertEqual(concept, "")
        mock_logger.warning.assert_called_with("No content provided to generate image prompt concept.")

    @patch("app.core.social.post.datetime")
    def test_get_daily_image_success(self, mock_datetime):
        # Mock today to be Monday
        mock_datetime.now.return_value.strftime.return_value = "Monday"

        # Create dummy image files
        with open(os.path.join(post.IMAGES_DIR, "monday.jpg"), "w") as f:
            f.write("dummy image data")

        image_path = post.get_daily_image(post.IMAGES_DIR)
        self.assertEqual(image_path, os.path.join(post.IMAGES_DIR, "monday.jpg"))

    @patch("app.core.social.post.datetime")
    def test_get_daily_image_fallback_to_random(self, mock_datetime):
        # Mock today to be Sunday, for which there is no image
        mock_datetime.now.return_value.strftime.return_value = "Sunday"

        # Create a random image to fallback to
        with open(os.path.join(post.IMAGES_DIR, "random.jpg"), "w") as f:
            f.write("dummy image data")

        image_path = post.get_daily_image(post.IMAGES_DIR)
        self.assertEqual(image_path, os.path.join(post.IMAGES_DIR, "random.jpg"))

    def test_get_daily_image_no_images(self):
        image_path = post.get_daily_image(post.IMAGES_DIR)
        self.assertEqual(image_path, "")

    @patch("app.core.social.post.logger")
    def test_get_daily_image_dir_not_found(self, mock_logger):
        shutil.rmtree(post.IMAGES_DIR)
        image_path = post.get_daily_image(post.IMAGES_DIR)
        self.assertEqual(image_path, "")
        mock_logger.error.assert_called_with(f"Image directory not found: {post.IMAGES_DIR}")

    @patch("app.core.social.post.graph")
    @patch("app.core.social.post.FACEBOOK_PAGE_ID", "test-page-id")
    @patch("app.core.social.post.requests")
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_post_to_facebook_success(self, mock_open, mock_requests, mock_graph):
        with patch("app.core.social.post.HEALTHCHECKS_PING_URL", "http://fake-url"):
            post.post_to_facebook("Test text", "test_image.jpg")
            mock_graph.put_photo.assert_called_once()
            mock_open.assert_called_once_with("test_image.jpg", "rb")

    @patch("app.core.social.post.logger")
    @patch("app.core.social.post.requests")
    @patch("app.core.social.post.FACEBOOK_PAGE_ID", "test-page-id")
    @patch("app.core.social.post.graph")
    def test_post_to_facebook_missing_data(self, mock_graph, mock_requests, mock_logger):
        with patch("app.core.social.post.HEALTHCHECKS_PING_URL", "http://fake-url"):
            post.post_to_facebook("", "test_image.jpg")
            mock_logger.error.assert_called_with("Missing necessary data for Facebook post. Aborting.")
            mock_graph.put_photo.assert_not_called()
            mock_requests.get.assert_called_once()  # healthcheck fail ping

    @patch("sys.exit")
    @patch("app.core.social.post.post_to_facebook")
    @patch("app.core.social.post.get_daily_image", return_value="image.jpg")
    @patch("app.core.social.post.generate_promotional_image", return_value="")
    @patch("app.core.social.post.create_facebook_post_text", return_value="post text")
    @patch("app.core.social.post.get_digest_content", return_value='{"content":"digest"}')
    def test_main_runs_full_process(
        self, mock_get_digest, mock_create_text, mock_generate_image, mock_get_image, mock_post_fb, mock_exit
    ):
        post.main()
        mock_get_digest.assert_called_once()
        mock_create_text.assert_called_once_with('{"content":"digest"}')
        mock_generate_image.assert_called_once_with('{"content":"digest"}')
        mock_get_image.assert_called_once()
        mock_post_fb.assert_called_once_with("post text", "image.jpg")
        mock_exit.assert_not_called()

    @patch("app.core.social.post.post_text_only_to_facebook")
    @patch("app.core.social.post.get_daily_image", return_value="")
    @patch("app.core.social.post.generate_promotional_image", return_value="")
    @patch("app.core.social.post.create_facebook_post_text", return_value="post text")
    @patch("app.core.social.post.get_digest_content", return_value='{"content":"digest"}')
    def test_main_text_only_when_no_image(
        self, mock_get_digest, mock_create_text, mock_generate_image, mock_get_image, mock_post_text_only
    ):
        post.main()
        mock_generate_image.assert_called_once()
        mock_get_image.assert_called_once()
        mock_post_text_only.assert_called_once_with("post text")

    @patch("sys.exit")
    @patch("app.core.social.post.post_to_facebook", return_value=False)
    @patch("app.core.social.post.get_daily_image", return_value="image.jpg")
    @patch("app.core.social.post.generate_promotional_image", return_value="")
    @patch("app.core.social.post.create_facebook_post_text", return_value="post text")
    @patch("app.core.social.post.get_digest_content", return_value='{"content":"digest"}')
    def test_main_exits_nonzero_when_facebook_post_fails(
        self, mock_get_digest, mock_create_text, mock_generate_image, mock_get_image, mock_post_fb, mock_exit
    ):
        # Regression test: an expired/invalid Facebook token (or any post failure)
        # must cause main() to exit non-zero, so `inv facebook-post` and cron.sh
        # correctly detect the failure instead of reporting success.
        post.main()
        mock_post_fb.assert_called_once_with("post text", "image.jpg")
        mock_exit.assert_called_once_with(1)

    @patch("sys.exit")
    @patch("app.core.social.post.post_text_only_to_facebook", return_value=False)
    @patch("app.core.social.post.get_daily_image", return_value="")
    @patch("app.core.social.post.generate_promotional_image", return_value="")
    @patch("app.core.social.post.create_facebook_post_text", return_value="post text")
    @patch("app.core.social.post.get_digest_content", return_value='{"content":"digest"}')
    def test_main_exits_nonzero_when_text_only_post_fails(
        self,
        mock_get_digest,
        mock_create_text,
        mock_generate_image,
        mock_get_image,
        mock_post_text_only,
        mock_exit,
    ):
        post.main()
        mock_post_text_only.assert_called_once_with("post text")
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
