import unittest
from unittest.mock import AsyncMock, patch

from tortoise import Tortoise

from app.core.db.models import Article
from app.core.news.fetch import save_news_to_db, save_news_to_file


class TestSaveToDB(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await Tortoise.init(
            db_url="sqlite://:memory:",
            modules={"models": ["app.core.db.models"]},
        )
        await Tortoise.generate_schemas(safe=True)

    async def asyncTearDown(self):
        await Tortoise.close_connections()
        await Tortoise._drop_databases()

    @patch("app.core.news.fetch.logging")
    async def test_save_news_to_db(self, mock_logging):
        mock_create = AsyncMock()
        Article.create = mock_create

        news = [
            {
                "source": "Example Site",
                "url": f"https://example.com/article-{i}",
                "title": f"News Article {i}",
                "content": f"Here's the content for article {i}",
            }
            for i in range(1, 4)
        ]
        await save_news_to_db(news)

        expected_calls = []
        for article in news:
            expected_calls.append(
                unittest.mock.call(
                    source=article["source"],
                    url=article["url"],
                    title=article["title"],
                    content=article["content"],
                ),
            )
        mock_create.assert_has_calls(expected_calls)

        self.assertEqual(mock_create.call_count, len(news))

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


if __name__ == "__main__":
    unittest.main()
