import unittest
from datetime import datetime
from unittest.mock import patch

from peewee import SqliteDatabase

from app.core.db.config import database as real_database
from app.core.db.models import Article
from app.core.news.fetch import get_latest_news, save_news_to_db, save_news_to_file

MODELS = [Article]
test_db = SqliteDatabase(":memory:")


class TestSaveToDB(unittest.TestCase):
    def setUp(self):
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        test_db.connect()
        test_db.create_tables(MODELS)

    def tearDown(self):
        # Not strictly necessary since SQLite in-memory databases only live
        # for the duration of the connection, and in the next step we close
        # the connection...but a good practice all the same.
        test_db.drop_tables(MODELS)

        # Close connection to db.
        test_db.close()

        # Re-bind to the real database - unittest discover runs every test
        # module in one process, and peewee's bind() mutates Article.Meta.database
        # globally, so leaving it on test_db here breaks any later test module
        # that needs the real Postgres connection (e.g. a pgvector integration test).
        real_database.bind(MODELS, bind_refs=False, bind_backrefs=False)

    @patch("app.core.news.fetch.embed_text")
    @patch("app.core.news.fetch.logging")
    @patch("app.core.db.models.Article.create")
    def test_save_news_to_db(self, mock_create, mock_logging, mock_embed_text):
        # @patch (not a raw `Article.create = ...` assignment) so this mock is
        # torn down after the test - unittest discover runs every test module
        # in one process, and a class-attribute assignment here would leave
        # Article.create permanently mocked for every later test module.
        mock_embed_text.return_value = [0.1, 0.2, 0.3]

        news = [
            {
                "source": "Example Site",
                "url": f"https://example.com/article-{i}",
                "title": f"News Article {i}",
                "content": f"Here's the content for article {i}",
            }
            for i in range(1, 4)
        ]

        result = save_news_to_db(news)

        self.assertEqual(set(result.keys()), {article["url"] for article in news})
        self.assertTrue(all(saved is mock_create.return_value for saved in result.values()))

        expected_calls = []
        for article in news:
            expected_calls.append(
                unittest.mock.call(
                    source=article["source"],
                    url=article["url"],
                    title=article["title"],
                    content=article["content"],
                    embedding=[0.1, 0.2, 0.3],
                ),
            )
        mock_create.assert_has_calls(expected_calls)

        self.assertEqual(mock_create.call_count, len(news))
        mock_embed_text.assert_any_call(news[0]["content"])

        mock_logging.info.assert_called_once_with("Saving news to the database ...")


class TestSaveToFile(unittest.TestCase):
    @patch("builtins.open")
    @patch("json.dump")
    def test_save_news_to_file(self, mock_json_dump, mock_open):
        news = [{"title": f"News {i}", "content": f"Content {i}"} for i in range(1, 4)]
        dest = "test.json"

        save_news_to_file(news, dest)

        mock_open.assert_called_once_with(dest, "w")
        mock_json_dump.assert_called_once_with(news, mock_open().__enter__(), indent=2, ensure_ascii=False)


class TestGetLatestNews(unittest.TestCase):
    @patch("app.core.news.fetch.today", datetime(2026, 9, 9).date())
    @patch("app.core.news.fetch.is_backfill", True)
    @patch("app.core.news.fetch.fetch_all")
    @patch("app.core.news.fetch.get_rss_feed_entries")
    @patch("app.core.news.fetch.get_news")
    def test_backfill_bounds_fetch_to_the_target_day(self, mock_get_news, mock_get_rss, mock_fetch_all):
        mock_fetch_all.return_value = [{"source": "News Diggers!", "url": "https://diggers.news/x", "title": "t"}]

        news = get_latest_news()

        mock_fetch_all.assert_called_once_with(datetime(2026, 9, 9), until=datetime(2026, 9, 10))
        mock_get_news.assert_not_called()
        mock_get_rss.assert_not_called()
        self.assertEqual(news, mock_fetch_all.return_value)

    @patch("app.core.news.fetch.is_backfill", False)
    @patch("app.core.news.fetch.fetch_all")
    @patch("app.core.news.fetch.get_rss_feed_entries")
    @patch("app.core.news.fetch.get_news")
    def test_live_day_uses_live_sources_not_historical_archive(self, mock_get_news, mock_get_rss, mock_fetch_all):
        mock_get_news.return_value = [{"source": "ZNBC", "url": "https://znbc.co.zm/x", "title": "z"}]
        mock_get_rss.return_value = [{"source": "News Diggers!", "url": "https://diggers.news/x", "title": "t"}]

        news = get_latest_news()

        mock_fetch_all.assert_not_called()
        self.assertEqual(news, mock_get_rss.return_value + mock_get_news.return_value)


if __name__ == "__main__":
    unittest.main()
