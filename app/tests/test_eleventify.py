import os
import shutil
import tempfile
import unittest
from datetime import timedelta
from unittest.mock import patch

from peewee import SqliteDatabase

from app.core.db.models import Article, Episode, Mp3
from app.core.podcast.eleventify import render_jinja_template
from app.core.utilities import lingo, podcast_host, today, today_human_readable, today_iso_fmt

MODELS = [Article, Episode, Mp3]
test_db = SqliteDatabase(":memory:")


class TestEleventify(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.dist_file = os.path.join(self.temp_dir, f"{today_iso_fmt}.njk")
        self.news_headlines = os.path.join(self.temp_dir, f"{today_iso_fmt}_news_headlines.txt")

        self.patch_dist_file = patch("app.core.podcast.eleventify.dist_file", self.dist_file)
        self.patch_news_headlines = patch("app.core.podcast.eleventify.news_headlines", self.news_headlines)

        self.patch_dist_file.start()
        self.patch_news_headlines.start()

        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        test_db.connect()
        test_db.create_tables(MODELS)

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

        articles = [
            {
                "title": f"Test Article {idx}",
                "source": f"Test Source {idx}",
                "url": f"https://example.com/{idx}",
                "content": f"This is a test article {idx}",
                "date": today,
                "episode": self.episode,
            }
            for idx in range(5)
        ]
        articles.append(
            {
                "title": "Test Article 5",
                "source": "Test Source 5",
                "url": "https://example.com/5",
                "content": "This is a test article 5",
                "date": today - timedelta(days=1),
            }
        )
        self.articles = [Article(**article) for article in articles]
        for article in self.articles:
            article.save()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        # Not strictly necessary since SQLite in-memory databases only live
        # for the duration of the connection, and in the next step we close
        # the connection...but a good practice all the same.
        test_db.drop_tables(MODELS)

        # Close connection to db.
        test_db.close()

        # If we wanted, we could re-bind the models to their original
        # database here. But for tests this is probably not necessary.

        self.patch_dist_file.stop()
        self.patch_news_headlines.stop()

    @patch("app.core.podcast.eleventify.get_content")
    @patch("app.core.podcast.eleventify.create_episode_summary")
    @patch("app.core.podcast.eleventify.logging")
    def test_render_jinja_template(self, mock_logging, mock_episode_summary, mock_get_content):
        mock_episode_summary.return_value = (
            "In today's news, we cover various topics, including the Lorem Ipsum incident, "
            "where a prankster replaced all traffic signs with memes, a study suggesting that "
            "talking to houseplants improves Wi-Fi signal strength, and an interview with a "
            "local squirrel who claims to have invented a new dance craze sweeping the forest floor."
        )
        mock_get_content.return_value = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        render_jinja_template(production_time=120, word_count=5000)

        mock_logging.info.assert_called_once_with("Rendering Jinja template ...")
        self.assertTrue(os.path.exists(self.dist_file))
        file_size = os.path.getsize(self.dist_file)
        self.assertNotEqual(file_size, 0, f"The file {self.dist_file} is empty.")
        with open(self.dist_file, "r") as f:
            content = f.read()

        for i in range(5):
            self.assertIn(f"Test Article {i}", content)
            self.assertIn(f"Test Source {i}", content)
            self.assertIn(f"https://example.com/{i}", content)

        for i in [5, 6]:
            self.assertNotIn(f"Test Article {i}", content)
            self.assertNotIn(f"Test Source {i}", content)
            self.assertNotIn(f"https://example.com/{i}", content)

        self.assertIn("including the Lorem Ipsum incident", content)
        self.assertIn('episode: "001"', content)
        self.assertIn(podcast_host, content)
        self.assertIn(lingo, content)
        self.assertIn(f"{today_iso_fmt}_podcast_dist.mp3", content)
        self.assertIn("production_time: 2 minutes", content)
        self.assertIn("count: 5,000", content)
        self.assertIn("size: 10.00 MB", content)
        self.assertIn("enclosure_length: 10485760", content)
        self.assertIn("itunes_duration: 10:30", content)
