import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import requests
from peewee import SqliteDatabase

from app.core.db.models import Article, Episode, Mp3
from app.core.social.post import (
    create_facebook_post,
    get_content,
    get_episode_number,
    get_random_image,
    get_random_video,
    podcast_is_live,
    post_to_facebook,
    upload_video_to_facebook,
)
from app.core.utilities import (
    lingo,
    podcast_host,
    today_human_readable,
    today_iso_fmt,
)

MODELS = [Article, Episode, Mp3]
test_db = SqliteDatabase(":memory:")


class TestSocialPost(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()

        # Create some temporary test files
        self.video_file = os.path.join(self.temp_dir, "test_video.mp4")
        self.image_file = os.path.join(self.temp_dir, "test_image.png")
        self.logo_file = os.path.join(self.temp_dir, "logo.png")

        # Create empty test files
        open(self.video_file, "w").close()
        open(self.image_file, "w").close()
        open(self.logo_file, "w").close()

        # Set up test database
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
        test_db.connect()
        test_db.create_tables(MODELS)

        # Create test data in database
        self.mp3 = Mp3.create(
            url=f"https://example.com/{today_iso_fmt}_podcast_dist.mp3", filesize=10485760, duration=630
        )

        self.episode = Episode.create(
            number=1,
            live=True,
            title=today_human_readable,
            description="Episode 001",
            presenter=podcast_host,
            locale=lingo.replace("-", "_"),
            mp3=self.mp3,
            time_to_produce=120,
            word_count=5000,
        )

        # Create test content file
        self.content_file = os.path.join(self.temp_dir, f"{today_iso_fmt}_podcast-content.txt")
        with open(self.content_file, "w") as f:
            f.write("Test podcast content")

        # Create headlines file
        self.headlines_file = os.path.join(self.temp_dir, f"{today_iso_fmt}_news_headlines.txt")
        with open(self.headlines_file, "w") as f:
            f.write("Title: Zed News Podcast episode 1\nTest headlines")

    def tearDown(self):
        # Remove temporary directory and files
        shutil.rmtree(self.temp_dir)

        # Clean up database
        test_db.drop_tables(MODELS)
        test_db.close()

    @patch("app.core.social.post.requests.head")
    def test_podcast_is_live(self, mock_head):
        # Test when podcast is live
        mock_head.return_value.status_code = 200
        self.assertTrue(podcast_is_live("https://example.com/episode/1"))

        # Test when podcast is not live
        mock_head.return_value.status_code = 404
        self.assertFalse(podcast_is_live("https://example.com/episode/2"))

        # Test when request fails
        mock_head.side_effect = requests.exceptions.RequestException
        self.assertFalse(podcast_is_live("https://example.com/episode/3"))

    def test_get_content(self):
        with patch("app.core.social.post.transcript", self.content_file):
            content = get_content()
            self.assertEqual(content, "Test podcast content")

    def test_get_episode_number(self):
        with patch("app.core.social.post.news_headlines", self.headlines_file):
            number = get_episode_number(self.headlines_file)
            self.assertEqual(number, "1")

    def test_get_random_video(self):
        # Test with existing video
        with patch("os.listdir") as mock_listdir, patch("os.path.isfile") as mock_isfile:
            mock_listdir.return_value = ["test1.mp4", "test2.mp4"]
            mock_isfile.return_value = True
            video = get_random_video(self.temp_dir)
            self.assertIsNotNone(video)
            self.assertTrue(video.endswith(".mp4"))

        # Test with no videos
        with patch("os.listdir") as mock_listdir:
            mock_listdir.return_value = ["test.txt", "test.jpg"]
            video = get_random_video(self.temp_dir)
            self.assertIsNone(video)

    def test_get_random_image(self):
        # Test with existing images
        with patch("os.listdir") as mock_listdir, patch("os.path.isfile") as mock_isfile:
            mock_listdir.return_value = ["test1.jpg", "test2.png"]
            mock_isfile.return_value = True
            image = get_random_image(self.temp_dir)
            self.assertIsNotNone(image)
            self.assertTrue(image.endswith((".jpg", ".png")))

        # Test with no images
        with patch("os.listdir") as mock_listdir:
            mock_listdir.return_value = ["test.txt", "test.mp4"]
            image = get_random_image(self.temp_dir)
            self.assertIsNone(image)

    @patch("app.core.social.post.client")
    def test_create_facebook_post(self, mock_client):
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "Test Facebook post content"
        mock_client.chat.completions.create.return_value = mock_completion

        result = create_facebook_post("Test content", "https://example.com")
        self.assertEqual(result, "Test Facebook post content")

    @patch("app.core.social.post.facebook.GraphAPI")
    def test_post_to_facebook(self, mock_graph_api):
        mock_graph = MagicMock()
        mock_graph_api.return_value = mock_graph

        post_to_facebook("Test content", "https://example.com")

        mock_graph.put_object.assert_called_once()
        args = mock_graph.put_object.call_args[1]
        self.assertEqual(args["message"], "Test content")
        self.assertEqual(args["link"], "https://example.com")

    @patch("app.core.social.post.requests.post")
    def test_upload_video_to_facebook(self, mock_post):
        # Test successful upload
        mock_post.return_value.json.return_value = {"id": "123456"}
        result = upload_video_to_facebook(self.video_file, title="Test Video", description="Test Description")
        self.assertEqual(result, "https://www.facebook.com/watch/?v=123456")

        # Test failed upload
        mock_post.return_value.json.return_value = {"error": "Upload failed"}
        result = upload_video_to_facebook(self.video_file, title="Test Video", description="Test Description")
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
