import asyncio
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from app.core.podcast.mix import extract_duration_in_milliseconds, mix_audio
from app.core.utilities import TEST_DIR, today_iso_fmt


class MockEpisodeQuerySet:
    def __init__(self, episodes):
        self.episodes = episodes

    async def count(self):
        return len(self.episodes)


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
        intro_audio_path = tempfile.NamedTemporaryFile(suffix=".mp3", dir=self.temp_dir, delete=False).name
        outro_audio_path = tempfile.NamedTemporaryFile(suffix=".mp3", dir=self.temp_dir, delete=False).name

        # Copy example audio files to temporary directory
        data_dir = TEST_DIR / "test_data"
        shutil.copyfile(data_dir / "example.mp3", example_audio_path)
        shutil.copyfile(data_dir / "intro.mp3", intro_audio_path)
        shutil.copyfile(data_dir / "outro.mp3", outro_audio_path)

        # Assign audio file paths for the test
        self.voice_track = example_audio_path
        self.intro_track = intro_audio_path
        self.outro_track = outro_audio_path
        self.dest = os.path.join(self.temp_dir, f"{today_iso_fmt}_podcast_dist.mp3")

    def tearDown(self):
        # Remove temporary directory and its contents
        shutil.rmtree(self.temp_dir)
        os.remove(self.dest)

    @patch("app.core.db.models.Episode.filter")
    def test_mix_audio(self, filter_mock):
        # Call the function
        episodes = [1, 2, 3]
        query_set_mock = MockEpisodeQuerySet(episodes)
        filter_mock.return_value = query_set_mock
        asyncio.run(mix_audio(self.voice_track, self.intro_track, self.outro_track, self.dest))

        # Assert that the output file exists
        self.assertTrue(os.path.exists(self.dest))


if __name__ == "__main__":
    unittest.main()
