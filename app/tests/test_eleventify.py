import os
import shutil
import tempfile
import unittest
from datetime import timedelta
from unittest.mock import patch

from tortoise import Tortoise

from app.core.db.models import MP3, Article, Episode
from app.core.podcast.eleventify import render_jinja_template
from app.core.utilities import lingo, podcast_host, today, today_human_readable, today_iso_fmt


class TestEleventify(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.dist_file = os.path.join(self.temp_dir, f"{today_iso_fmt}.njk")

        self.patcher = patch("app.core.podcast.eleventify.dist_file", self.dist_file)
        self.patcher.start()

        await Tortoise.init(
            db_url="sqlite://:memory:",
            modules={"models": ["app.core.db.models"]},
        )
        await Tortoise.generate_schemas(safe=True)

        self.mp3 = MP3(url=f"https://example.com/{today_iso_fmt}_podcast_dist.mp3", filesize=10485760, duration=630)
        await self.mp3.save()

        self.episode = Episode(
            number=1,
            title=today_human_readable,
            description="Episode 001",
            presenter=podcast_host,
            locale=lingo.replace("-", "_"),
            mp3=self.mp3,
            time_to_produce=120,
            word_count=5000,
        )
        await self.episode.save()

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
        await Article.bulk_create(self.articles)

    async def asyncTearDown(self):
        shutil.rmtree(self.temp_dir)
        await Tortoise.close_connections()
        await Tortoise._drop_databases()
        self.patcher.stop()

    @patch("app.core.podcast.eleventify.logging")
    async def test_render_jinja_template(self, mock_logging):
        await render_jinja_template(production_time=120, word_count=5000)

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

        self.assertIn(today_human_readable, content)
        self.assertIn('episode: "001"', content)
        self.assertIn(podcast_host, content)
        self.assertIn(lingo, content)
        self.assertIn(f"{today_iso_fmt}_podcast_dist.mp3", content)
        self.assertIn("production_time: 2 minutes", content)
        self.assertIn("count: 5,000", content)
        self.assertIn("size: 10.00 MB", content)
        self.assertIn("enclosure_length: 10485760", content)
        self.assertIn("itunes_duration: 10:30", content)
