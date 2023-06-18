import asyncio
import datetime
import unittest
from unittest.mock import patch

from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

from app.core.db.models import Article
from app.core.podcast.content import (
    get_episode_number,
    random_dig_in,
    random_intro,
    random_outro,
    update_article_with_summary,
)


class MockEpisodeQuerySet:
    def __init__(self, episodes):
        self.episodes = episodes

    async def count(self):
        return len(self.episodes)


class TestEpisodeNumber(unittest.TestCase):
    @patch("app.core.db.models.Episode.filter")
    def test_get_episode_number(self, filter_mock):
        # Create a custom mock object with a count method
        episodes = [1, 2, 3]
        query_set_mock = MockEpisodeQuerySet(episodes)
        filter_mock.return_value = query_set_mock

        # Run the function
        result = asyncio.run(get_episode_number())

        # Assert the result
        self.assertEqual(result, 4)


class TestArticleUpdate(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Set up the test database connection
        await Tortoise.init(
            db_url="sqlite://:memory:",  # SQLite in-memory database
            modules={"models": ["app.core.db.models"]},
        )
        await Tortoise.generate_schemas(safe=True)

        # Create a mock article for testing
        self.mock_article = Article(
            title="Test Article",
            source="Test Source",
            url="http://example.com",
            content="This is a test article",
            date=datetime.date.today(),
        )
        await self.mock_article.save()

    async def asyncTearDown(self):
        # Clean up the mock article and close the test database connection
        await self.mock_article.delete()
        await Tortoise.close_connections()
        await Tortoise._drop_databases()

    async def test_update_article_with_summary(self):
        self.assertIsNone(self.mock_article.summary)
        self.assertEqual(await Article.all().count(), 1)
        # Call the function with the necessary arguments
        await update_article_with_summary(
            title="Test Article", url="http://example.com", date=datetime.date.today(), summary="This is a test summary"
        )
        # Retrieve the updated article from the database
        updated_article = await Article.get(title="Test Article", url="http://example.com", date=datetime.date.today())
        # Assert that the summary has been updated
        self.assertEqual(updated_article.summary, "This is a test summary")
        self.assertEqual(await Article.all().count(), 1)

    async def test_update_article_with_summary_article_not_found(self):
        # Call the function with an article that doesn't exist in the database
        with self.assertRaises(DoesNotExist):
            await update_article_with_summary(
                title="Non-existent Article",
                url="http://example.com",
                date=datetime.date.today(),
                summary="This article doesn't exist",
            )


class TestRandomContent(unittest.TestCase):
    def test_random_intro(self):
        result = random_intro()
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, "")

    def test_random_dig_in(self):
        result = random_dig_in()
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, "")

    def test_random_outro(self):
        result = random_outro()
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, "")


if __name__ == "__main__":
    unittest.main()
