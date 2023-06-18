import unittest
from datetime import timedelta
from unittest.mock import AsyncMock, patch

from tortoise import Tortoise

from app.core.db.models import MP3, Article, Episode
from app.core.podcast.episode import add_articles_to_episode, add_episode_to_db
from app.core.utilities import lingo, podcast_host, today, today_human_readable, today_iso_fmt


class TestEpisodeInDB(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await Tortoise.init(
            db_url="sqlite://:memory:",
            modules={"models": ["app.core.db.models"]},
        )
        await Tortoise.generate_schemas(safe=True)

        self.mp3 = MP3(url=f"http://example.com/{today_iso_fmt}_podcast_dist.mp3", filesize=10000, duration=3600)
        await self.mp3.save()

    async def asyncTearDown(self):
        await Tortoise.close_connections()
        await Tortoise._drop_databases()

    @patch("app.core.podcast.episode.logging")
    async def test_add_episode_to_db(self, mock_logging):
        mock_create = AsyncMock()
        Episode.create = mock_create

        await add_episode_to_db(3600, 5000)

        mock_create.assert_awaited_once_with(
            number=1,
            title=today_human_readable,
            description="Episode 001",
            presenter=podcast_host,
            locale=lingo.replace("-", "_"),
            mp3=self.mp3,
            word_count=3600,
            time_to_produce=5000,
        )
        mock_logging.info.assert_called_once_with("Adding episode 001 to the database")


class TestArticlesInDB(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await Tortoise.init(
            db_url="sqlite://:memory:",
            modules={"models": ["app.core.db.models"]},
        )
        await Tortoise.generate_schemas(safe=True)

        self.mp3 = MP3(url=f"http://example.com/{today_iso_fmt}_podcast_dist.mp3", filesize=10000, duration=3600)
        await self.mp3.save()

        self.episode = Episode(
            number=1,
            title=today_human_readable,
            description="Episode 001",
            presenter=podcast_host,
            locale=lingo.replace("-", "_"),
            mp3=self.mp3,
            time_to_produce=3600,
            word_count=5000,
        )
        await self.episode.save()

        articles = [
            {
                "title": f"Test Article {idx}",
                "source": f"Test Source {idx}",
                "url": f"http://example.com/{idx}",
                "content": f"This is a test article {idx}",
                "date": today,
            }
            for idx in range(5)
        ]
        articles.append(
            {
                "title": "Test Article 5",
                "source": "Test Source 5",
                "url": "http://example.com/6",
                "content": "This is a test article 5",
                "date": today - timedelta(days=1),
            }
        )
        self.articles = [Article(**article) for article in articles]
        await Article.bulk_create(self.articles)

    async def asyncTearDown(self):
        await Tortoise.close_connections()
        await Tortoise._drop_databases()

    @patch("app.core.podcast.episode.logging")
    async def test_add_articles_to_episode(self, mock_logging):
        episode = await Episode.get(number=1)
        self.assertEqual(episode.live, False)
        self.assertEqual(await episode.articles.all().count(), 0)
        for article in await Article.filter(date=today):
            self.assertIsNone(await article.episode)

        await add_articles_to_episode()
        updated_episode = await Episode.filter(number=1).first()

        self.assertEqual(updated_episode.live, True)
        self.assertEqual(await updated_episode.articles.all().count(), 5)
        mock_logging.info.assert_called_once_with("Updating articles for episode 001 ...")
        for article in await Article.filter(date=today):
            self.assertTrue(await article.episode, updated_episode)


if __name__ == "__main__":
    unittest.main()
