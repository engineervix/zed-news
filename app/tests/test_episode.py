import unittest
from datetime import timedelta
from unittest.mock import MagicMock, patch

from peewee import SqliteDatabase

from app.core.db.models import Article, Episode, Mp3
from app.core.podcast.episode import add_articles_to_episode, add_episode_to_db
from app.core.utilities import lingo, podcast_host, today, today_human_readable, today_iso_fmt

MODELS = [Article, Episode, Mp3]
test_db = SqliteDatabase(":memory:")


class TestEpisodeInDB(unittest.TestCase):
    def setUp(self):
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        test_db.connect()
        test_db.create_tables(MODELS, safe=True)

        self.mp3 = Mp3(url=f"http://example.com/{today_iso_fmt}_podcast_dist.mp3", filesize=10000, duration=3600)
        self.mp3.save()

    def tearDown(self):
        # Not strictly necessary since SQLite in-memory databases only live
        # for the duration of the connection, and in the next step we close
        # the connection...but a good practice all the same.
        test_db.drop_tables(MODELS)

        # Close connection to db.
        test_db.close()

        # If we wanted, we could re-bind the models to their original
        # database here. But for tests this is probably not necessary.

    @patch("app.core.podcast.episode.logging")
    def test_add_episode_to_db(self, mock_logging):
        mock_create = MagicMock()
        Episode.create = mock_create

        add_episode_to_db(3600, 5000)

        mock_create.assert_called_once_with(
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


class TestArticlesInDB(unittest.TestCase):
    def setUp(self):
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        test_db.connect()
        test_db.create_tables(MODELS, safe=True)

        self.mp3 = Mp3.create(url=f"http://example.com/{today_iso_fmt}_podcast_dist.mp3", filesize=10000, duration=3600)

        self.episode = Episode.create(
            number=1,
            title=today_human_readable,
            description="Episode 001",
            presenter=podcast_host,
            locale=lingo.replace("-", "_"),
            mp3=self.mp3,
            time_to_produce=3600,
            word_count=5000,
        )

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
        for article in self.articles:
            article.save()

    def tearDown(self):
        # Not strictly necessary since SQLite in-memory databases only live
        # for the duration of the connection, and in the next step we close
        # the connection...but a good practice all the same.
        test_db.drop_tables(MODELS)

        # Close connection to db.
        test_db.close()

        # If we wanted, we could re-bind the models to their original
        # database here. But for tests this is probably not necessary.

    @patch("app.core.podcast.episode.logging")
    def test_add_articles_to_episode(self, mock_logging):
        episode = Episode.select().where(Episode.number == 1).first()
        self.assertEqual(episode.live, False)
        self.assertEqual(episode.articles.count(), 0)
        for article in Article.select().where(Article.date == today):
            self.assertIsNone(article.episode)

        add_articles_to_episode()
        updated_episode = Episode.select().where(Episode.number == 1).first()

        self.assertEqual(updated_episode.live, True)
        self.assertEqual(updated_episode.articles.count(), 5)
        mock_logging.info.assert_called_once_with("Updating articles for episode 001 ...")
        for article in Article.select().where(Article.date == today):
            self.assertTrue(article.episode, updated_episode)


if __name__ == "__main__":
    unittest.main()
