import datetime
import os
import shutil
import tempfile
import unittest

from peewee import SqliteDatabase

from app.core.db.models import Article, Episode, Mp3
from app.core.podcast.mix import extract_duration_in_milliseconds, mix_audio
from app.core.utilities import TEST_DIR, lingo, podcast_host, today_human_readable, today_iso_fmt

MODELS = [Article, Episode, Mp3]
test_db = SqliteDatabase(":memory:")


class TestDurationExtraction(unittest.TestCase):
    def test_valid_output(self):
        output = "Duration: 00:01:23.456"
        expected_duration = 83450
        self.assertEqual(extract_duration_in_milliseconds(output), expected_duration)

    def test_invalid_output(self):
        output = "Invalid output"
        self.assertEqual(extract_duration_in_milliseconds(output), 0)

    def test_missing_duration(self):
        output = "Some other output"
        self.assertEqual(extract_duration_in_milliseconds(output), 0)

    def test_duration_with_zero_padding(self):
        output = "Duration: 00:00:09.001"
        expected_duration = 9000
        self.assertEqual(extract_duration_in_milliseconds(output), expected_duration)

    def test_large_duration(self):
        output = "Duration: 11:59:59.999"
        expected_duration = 43199990
        self.assertEqual(extract_duration_in_milliseconds(output), expected_duration)

    def test_duration_with_microseconds(self):
        output = "Duration: 00:00:01.123456"
        expected_duration = 1120
        self.assertEqual(extract_duration_in_milliseconds(output), expected_duration)

    def test_duration_with_additional_output(self):
        output = "Additional output Duration: 00:00:01.234"
        expected_duration = 1230
        self.assertEqual(extract_duration_in_milliseconds(output), expected_duration)


class TestMixAudio(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()

        # Create example audio files
        example_audio_path = tempfile.NamedTemporaryFile(suffix=".mp3", dir=self.temp_dir, delete=False).name
        background_audio_path = tempfile.NamedTemporaryFile(suffix=".mp3", dir=self.temp_dir, delete=False).name

        # Copy example audio files to temporary directory
        data_dir = TEST_DIR / "test_data"
        shutil.copyfile(data_dir / "example.mp3", example_audio_path)
        shutil.copyfile(data_dir / "background.mp3", background_audio_path)

        # Assign audio file paths for the test
        self.voice_track = example_audio_path
        self.music_track = background_audio_path
        self.dest = os.path.join(self.temp_dir, f"{today_iso_fmt}_podcast_dist.mp3")

        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        test_db.connect()
        test_db.create_tables(MODELS)

        # Create a mock article for testing
        self.mock_article = Article(
            title="Test Article",
            source="Test Source",
            url="http://example.com",
            content="This is a test article",
            date=datetime.date.today(),
        )
        self.mock_article.save()

        self.mp3 = Mp3(url=f"https://example.com/{today_iso_fmt}_podcast_dist.mp3", filesize=10485760, duration=630)
        self.mp3.save()

        self.episode = Episode(
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
        self.episode.save()

        self.mock_article.episode = self.episode
        self.mock_article.save()

    def tearDown(self):
        # Remove temporary directory and its contents
        shutil.rmtree(self.temp_dir)

        # Not strictly necessary since SQLite in-memory databases only live
        # for the duration of the connection, and in the next step we close
        # the connection...but a good practice all the same.
        test_db.drop_tables(MODELS)

        # Close connection to db.
        test_db.close()

        # If we wanted, we could re-bind the models to their original
        # database here. But for tests this is probably not necessary.

    def test_mix_audio(self):
        mix_audio(self.voice_track, self.music_track, self.dest)

        # Assert that the output file exists
        self.assertTrue(os.path.exists(self.dest))


if __name__ == "__main__":
    unittest.main()
