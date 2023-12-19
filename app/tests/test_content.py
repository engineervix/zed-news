import datetime

# import os
# import shutil
# import tempfile
import unittest
from unittest.mock import patch

# from unittest.mock import call, patch
from peewee import SqliteDatabase

from app.core.db.models import Article, Episode, Mp3
from app.core.podcast.content import (
    # create_transcript,
    get_episode_number,
    update_article_with_summary,
)
from app.core.utilities import lingo, podcast_host, today_human_readable, today_iso_fmt

MODELS = [Article, Episode, Mp3]
test_db = SqliteDatabase(":memory:")


class TestEpisodeNumber(unittest.TestCase):
    def setUp(self):
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        test_db.connect()
        test_db.create_tables(MODELS)

        # Create a mock article for testing
        self.mock_article = Article.create(
            title="Test Article",
            source="Test Source",
            url="http://example.com",
            content="This is a test article",
            date=datetime.date.today(),
        )

        self.mp3 = Mp3.create(
            url=f"https://example.com/{today_iso_fmt}_podcast_dist.mp3", filesize=10485760, duration=630
        )

        self.episode = Episode.create(
            number=21,
            live=True,
            title=today_human_readable,
            description="Episode 021",
            presenter=podcast_host,
            locale=lingo.replace("-", "_"),
            mp3=self.mp3,
            time_to_produce=120,
            word_count=5000,
        )

        self.mock_article.episode = self.episode
        self.mock_article.save()

    def tearDown(self):
        # Not strictly necessary since SQLite in-memory databases only live
        # for the duration of the connection, and in the next step we close
        # the connection...but a good practice all the same.
        test_db.drop_tables(MODELS)

        # Close connection to db.
        test_db.close()

        # If we wanted, we could re-bind the models to their original
        # database here. But for tests this is probably not necessary.

    def test_get_episode_number(self):
        # Run the function
        result = get_episode_number()

        # Assert the result
        self.assertEqual(result, 2)


class TestArticleUpdate(unittest.TestCase):
    def setUp(self):
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        test_db.connect()
        test_db.create_tables(MODELS)

        # Create a mock article for testing
        self.mock_article = Article.create(
            title="Test Article",
            source="Test Source",
            url="http://example.com",
            content="This is a test article",
            date=datetime.date.today(),
        )

    def tearDown(self):
        # Not strictly necessary since SQLite in-memory databases only live
        # for the duration of the connection, and in the next step we close
        # the connection...but a good practice all the same.
        test_db.drop_tables(MODELS)

        # Close connection to db.
        test_db.close()

        # If we wanted, we could re-bind the models to their original
        # database here. But for tests this is probably not necessary.

    def test_update_article_with_summary(self):
        self.assertIsNone(self.mock_article.summary)
        self.assertEqual(Article.select().count(), 1)
        # Call the function with the necessary arguments
        update_article_with_summary(
            title="Test Article", url="http://example.com", date=datetime.date.today(), summary="This is a test summary"
        )
        # Retrieve the updated article from the database
        updated_article = (
            Article.select()
            .where(
                (Article.title == "Test Article")
                & (Article.url == "http://example.com")
                & (Article.date == datetime.date.today())
            )
            .first()
        )
        # Assert that the summary has been updated
        self.assertEqual(updated_article.summary, "This is a test summary")
        self.assertEqual(Article.select().count(), 1)

    @patch("app.core.podcast.content.logging")
    def test_update_article_with_summary_article_not_found(self, mock_logging):
        data = {
            "title": "Non-existent Article",
            "url": "https://example.com",
            "date": datetime.date.today(),
            "summary": "This article doesn't exist",
        }

        # Call the function with an article that doesn't exist in the database
        update_article_with_summary(**data)
        # Assert that the function logged a warning
        mock_logging.warning.assert_called_once_with(
            f"Could not find article with title '{data['title']}', URL '{data['url']}', and date '{data['date']}'"
        )


# class TestTranscriptCreation(unittest.TestCase):
#     def setUp(self):
#         self.temp_dir = tempfile.mkdtemp()
#         self.text_file = os.path.join(self.temp_dir, "transcript_test.txt")

#         # Bind model classes to test db. Since we have a complete list of
#         # all models, we do not need to recursively bind dependencies.
#         test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

#         test_db.connect()
#         test_db.create_tables(MODELS)

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
#             Article(**data).save()

#     def tearDown(self):
#         shutil.rmtree(self.temp_dir)

#         # Not strictly necessary since SQLite in-memory databases only live
#         # for the duration of the connection, and in the next step we close
#         # the connection...but a good practice all the same.
#         test_db.drop_tables(MODELS)

#         # Close connection to db.
#         test_db.close()

#         # If we wanted, we could re-bind the models to their original
#         # database here. But for tests this is probably not necessary.

#     @patch("app.core.podcast.content.get_episode_number")
#     @patch("app.core.summarization.backends.openai.summarize")
#     def test_create_transcript_with_openai(self, mock_summarizer, mock_get_episode_number):
#         mock_get_episode_number.return_value = 22
#         summary = "This is a summary of the content"
#         mock_summarizer.return_value = summary

#         destination = self.text_file
#         news = self.article_data

#         create_transcript(news, destination, mock_summarizer)

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

#         create_transcript(news, destination, mock_summarizer)

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

#         create_transcript(news, destination, mock_summarizer)

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
