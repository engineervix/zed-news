import asyncio
import datetime
import unittest
from unittest.mock import patch

from tortoise import Tortoise

from app.core.db.models import Article
from app.core.podcast.content import (
    get_episode_number,
    update_article_with_summary,
)

# from app.core.podcast.content import create_transcript


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

    @patch("app.core.podcast.content.logging")
    async def test_update_article_with_summary_article_not_found(self, mock_logging):
        data = {
            "title": "Non-existent Article",
            "url": "https://example.com",
            "date": datetime.date.today(),
            "summary": "This article doesn't exist",
        }

        # Call the function with an article that doesn't exist in the database
        await update_article_with_summary(**data)
        # Assert that the function logged a warning
        mock_logging.warning.assert_called_once_with(
            f"Could not find article with title '{data['title']}', URL '{data['url']}', and date '{data['date']}'"
        )


# class TestTranscriptCreation(unittest.IsolatedAsyncioTestCase):
#     async def asyncSetUp(self):
#         self.temp_dir = tempfile.mkdtemp()
#         self.text_file = os.path.join(self.temp_dir, "transcript_test.txt")

#         # Set up the test database connection
#         await Tortoise.init(
#             db_url="sqlite://:memory:",  # SQLite in-memory database
#             modules={"models": ["app.core.db.models"]},
#         )
#         await Tortoise.generate_schemas(safe=True)

#         self.article_data = [
#             {
#                 "source": "Source 1",
#                 "url": "https://example.com/news-1",
#                 "title": "News 1",
#                 "content": "Content 1",
#                 "category": "",
#             },
#             {
#                 "source": "Source 2",
#                 "url": "https://website.com/news-2",
#                 "title": "News 2",
#                 "content": "Content 2",
#                 "category": "",
#             },
#             {
#                 "source": "Source 2",
#                 "url": "https://website.com/news-3",
#                 "title": "News 3",
#                 "content": "Content 3",
#                 "category": "",
#             },
#             {
#                 "source": "Source 3",
#                 "url": "https://anothersite.co.zm/news-4",
#                 "title": "News 4",
#                 "content": "Content 4",
#                 "category": "Sports",
#             },
#         ]

#         # add more articles so that Source 3 has 10 articles
#         for i in range(len(self.article_data) + 1, 14):
#             self.article_data.append(
#                 {
#                     "source": "Source 3",
#                     "url": f"https://anothersite.co.zm/news-{i}",
#                     "title": f"News {i}",
#                     "content": f"Content {i}",
#                     "category": "Sports",
#                 }
#             )

#         for data in self.article_data:
#             await Article(**data).save()

#     async def asyncTearDown(self):
#         shutil.rmtree(self.temp_dir)

#         await Tortoise.close_connections()
#         await Tortoise._drop_databases()

#     @patch("app.core.podcast.content.get_episode_number")
#     @patch("app.core.summarization.backends.openai.summarize")
#     def test_create_transcript_with_openai(self, mock_summarizer, mock_get_episode_number):
#         mock_get_episode_number.return_value = 22
#         summary = "This is a summary of the content"
#         mock_summarizer.return_value = summary

#         destination = self.text_file
#         news = self.article_data

#         asyncio.run(create_transcript(news, destination, mock_summarizer))

#         with open(destination, "r") as file:
#             transcript_content = file.read()

#         expected_calls = [call(item["content"], item["title"]) for item in news]

#         mock_summarizer.assert_has_calls(expected_calls)
#         self.assertIn(summary, transcript_content)
#         self.assertEqual(len(news), transcript_content.count(summary))
#         self.assertIn("We are going to start with news from", transcript_content)
#         self.assertIn("Next up, we have news from", transcript_content)
#         self.assertIn("To wrap up today's edition", transcript_content)
#         self.assertIn(today_human_readable, transcript_content)
#         self.assertIn("twenty-second", transcript_content)

#     @patch("app.core.podcast.content.get_episode_number")
#     @patch("app.core.summarization.backends.cohere.summarize")
#     def test_create_transcript_with_cohere(self, mock_summarizer, mock_get_episode_number):
#         mock_get_episode_number.return_value = 11
#         summary = "This is a summary of the content"
#         mock_summarizer.return_value = summary

#         destination = self.text_file
#         news = self.article_data

#         asyncio.run(create_transcript(news, destination, mock_summarizer))

#         with open(destination, "r") as file:
#             transcript_content = file.read()

#         expected_calls = [call(item["content"], item["title"]) for item in news]

#         mock_summarizer.assert_has_calls(expected_calls)
#         self.assertIn(summary, transcript_content)
#         self.assertEqual(len(news), transcript_content.count(summary))
#         self.assertIn("We are going to start with news from", transcript_content)
#         self.assertIn("Next up, we have news from", transcript_content)
#         self.assertIn("To wrap up today's edition", transcript_content)
#         self.assertIn(today_human_readable, transcript_content)
#         self.assertIn("eleventh", transcript_content)

#     @patch("app.core.podcast.content.get_episode_number")
#     @patch("app.core.summarization.backends.together.summarize")
#     def test_create_transcript_with_together(self, mock_summarizer, mock_get_episode_number):
#         mock_get_episode_number.return_value = 8
#         summary = "This is a summary of the content"
#         mock_summarizer.return_value = summary

#         destination = self.text_file
#         news = self.article_data

#         asyncio.run(create_transcript(news, destination, mock_summarizer))

#         with open(destination, "r") as file:
#             transcript_content = file.read()

#         expected_calls = [call(item["content"], item["title"]) for item in news]

#         mock_summarizer.assert_has_calls(expected_calls)
#         self.assertIn(summary, transcript_content)
#         self.assertEqual(len(news), transcript_content.count(summary))
#         self.assertIn("We are going to start with news from", transcript_content)
#         self.assertIn("Next up, we have news from", transcript_content)
#         self.assertIn("To wrap up today's edition", transcript_content)
#         self.assertIn(today_human_readable, transcript_content)
#         self.assertIn("eighth", transcript_content)


if __name__ == "__main__":
    unittest.main()
