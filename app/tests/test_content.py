import datetime
import unittest
from unittest.mock import MagicMock, patch

from peewee import SqliteDatabase

from app.core.db.models import Article, Episode, Mp3
from app.core.podcast.content import (
    create_transcript,
    get_episode_number,
    is_special_milestone,
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


class TestPodcastContent(unittest.TestCase):
    def setUp(self):
        """Set up test database before each test"""
        # Bind model classes to test db
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        # Connect to database and create tables
        test_db.connect()
        test_db.create_tables(MODELS)

        # Sample data for tests
        self.sample_news = [
            {
                "source": "Test Source 1",
                "url": "http://test1.com",
                "title": "Test Title 1",
                "content": "Test Content 1",
                "category": "News",
            },
            {
                "source": "Test Source 2",
                "url": "http://test2.com",
                "title": "Test Title 2",
                "content": "Test Content 2",
                "category": "Sports",
            },
        ]

        # Create a sample episode and mp3 for testing
        self.mp3 = Mp3.create(url="http://example.com/test.mp3", filesize=1000, duration=300)
        self.episode = Episode.create(
            number=1,
            live=True,
            title="Test Episode",
            description="Test Description",
            presenter="Test Presenter",
            locale="en_ZA",
            mp3=self.mp3,
            time_to_produce=60,
            word_count=1000,
        )

    def tearDown(self):
        """Clean up test database after each test"""
        test_db.drop_tables(MODELS)
        test_db.close()

    def test_is_special_milestone(self):
        """Test special milestone detection"""
        self.assertTrue(is_special_milestone(50))
        self.assertTrue(is_special_milestone(100))
        self.assertFalse(is_special_milestone(49))
        self.assertFalse(is_special_milestone(51))

    def test_get_episode_number(self):
        """Test episode number generation"""
        # Since we created one episode in setUp, next number should be 2
        self.assertEqual(get_episode_number(), 2)

    @patch("app.core.podcast.content.logging")
    def test_update_article_with_nonexistent_article(self, mock_logging):
        """Test updating summary for non-existent article"""
        update_article_with_summary(
            title="Non-existent", url="http://test.com", date=datetime.date.today(), summary="Test Summary"
        )
        mock_logging.warning.assert_called_once()

    def test_update_article_with_summary(self):
        """Test article summary updates"""
        article = Article.create(
            title="Test Title",
            url="http://test.com",
            source="Test Source",
            content="Test Content",
            date=datetime.date.today(),
        )

        update_article_with_summary(
            title="Test Title", url="http://test.com", date=datetime.date.today(), summary="Updated Summary"
        )

        updated_article = Article.get(Article.id == article.id)
        self.assertEqual(updated_article.summary, "Updated Summary")

    @patch("app.core.podcast.content.OpenAI")
    def test_create_transcript(self, mock_openai):
        """Test transcript creation"""
        # Setup mock for OpenAI
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "Test transcript"
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        # Mock summarizer function
        mock_summarizer = MagicMock(return_value="Summarized content")

        # Test
        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            create_transcript(self.sample_news, "test_transcript.txt", mock_summarizer)

        # Verify
        mock_summarizer.assert_called()
        self.assertEqual(mock_summarizer.call_count, len(self.sample_news))
        mock_file().write.assert_called()

    @patch("app.core.podcast.content.OpenAI")
    def test_create_transcript_with_empty_news(self, mock_openai):
        """Test transcript creation with empty news list"""
        # Setup mock for OpenAI
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "Test generic content"
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        mock_summarizer = MagicMock()

        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            create_transcript([], "test_transcript.txt", mock_summarizer)

        # Verify
        mock_summarizer.assert_not_called()

        # GPT should have been called to generate content for empty news
        mock_openai.return_value.chat.completions.create.assert_called_once()

        # Verify the GPT-generated content was written to file
        mock_file().write.assert_called_with("Test generic content")


if __name__ == "__main__":
    unittest.main()
