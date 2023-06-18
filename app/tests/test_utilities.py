import os
import unittest
from datetime import datetime
from unittest.mock import patch

from app.core.utilities import (
    convert_seconds_to_mmss,
    count_words,
    custom_strftime,
    delete_file,
    format_duration,
    format_filesize,
    is_valid_date,
    suffix,
    words_per_minute,
)


class TestUtilities(unittest.TestCase):
    def setUp(self):
        self.file_path = "test_file.txt"

    def tearDown(self):
        # Clean up the test file after each test
        try:
            os.remove(self.file_path)
        except FileNotFoundError:
            pass

    def test_delete_file(self):
        # Create a test file
        with open(self.file_path, "w") as file:
            file.write("Test content")

        # Delete the file
        delete_file(self.file_path)

        # Assert that the file is deleted
        self.assertFalse(os.path.exists(self.file_path))

    def test_format_duration(self):
        # Test with duration of 90 seconds
        duration_string = format_duration(90)
        self.assertEqual(duration_string, "1 minute, 30 seconds")

        # Test with duration of 60 seconds
        duration_string = format_duration(60)
        self.assertEqual(duration_string, "1 minute")

        # Test with duration of 45 seconds
        duration_string = format_duration(45)
        self.assertEqual(duration_string, "45 seconds")

    def test_words_per_minute(self):
        # Test with duration of 300 seconds (5 minutes) and word count of 150
        words_per_min = words_per_minute(300, 150)
        self.assertEqual(words_per_min, "30 words per minute")

        # Test with duration of 0 seconds and word count of 100
        words_per_min = words_per_minute(0, 100)
        self.assertEqual(words_per_min, "0 words per minute")

    def test_convert_seconds_to_mmss(self):
        # Test with duration of 65 seconds
        mmss = convert_seconds_to_mmss(65)
        self.assertEqual(mmss, "01:05")

        # Test with duration of 120 seconds
        mmss = convert_seconds_to_mmss(120)
        self.assertEqual(mmss, "02:00")

        # Test with duration of 3600 seconds (1 hour)
        mmss = convert_seconds_to_mmss(3600)
        self.assertEqual(mmss, "60:00")

    def test_format_filesize(self):
        # Test with filesize of 2048 bytes
        filesize_str = format_filesize(2048)
        self.assertEqual(filesize_str, "2.00 KB")

        # Test with filesize of 1024 bytes
        filesize_str = format_filesize(1024)
        self.assertEqual(filesize_str, "1.00 KB")

        # Test with filesize of 1048576 bytes (1 MB)
        filesize_str = format_filesize(1048576)
        self.assertEqual(filesize_str, "1.00 MB")

        # Test with filesize of 5368709120 bytes (5 GB)
        filesize_str = format_filesize(5368709120)
        self.assertEqual(filesize_str, "5.00 GB")

    def test_is_valid_date(self):
        # Test with a valid date string
        valid_date = is_valid_date("2022-01-01")
        self.assertTrue(valid_date)

        # Test with an invalid date string
        invalid_date = is_valid_date("2022-13-01")
        self.assertFalse(invalid_date)

        # Test with an invalid date format
        invalid_date_format = is_valid_date("01-01-2022")
        self.assertFalse(invalid_date_format)

    def test_suffix(self):
        self.assertEqual(suffix(1), "st")
        self.assertEqual(suffix(2), "nd")
        self.assertEqual(suffix(3), "rd")
        self.assertEqual(suffix(4), "th")
        self.assertEqual(suffix(11), "th")
        self.assertEqual(suffix(12), "th")
        self.assertEqual(suffix(13), "th")
        self.assertEqual(suffix(21), "st")
        self.assertEqual(suffix(22), "nd")
        self.assertEqual(suffix(23), "rd")
        self.assertEqual(suffix(24), "th")

    def test_custom_strftime(self):
        # Mock the datetime object for testing
        with patch("app.core.utilities.datetime") as mock_datetime:
            mock_datetime.strftime.return_value = "2023-06-{S}"

            # Test with day 1
            formatted_date = custom_strftime("%Y-%m-{S}", datetime(2023, 6, 1))
            self.assertEqual(formatted_date, "2023-06-1st")

            # Test with day 2
            formatted_date = custom_strftime("%Y-%m-{S}", datetime(2023, 6, 2))
            self.assertEqual(formatted_date, "2023-06-2nd")

            # Test with day 3
            formatted_date = custom_strftime("%Y-%m-{S}", datetime(2023, 6, 3))
            self.assertEqual(formatted_date, "2023-06-3rd")

            # Test with day 4
            formatted_date = custom_strftime("%Y-%m-{S}", datetime(2023, 6, 4))
            self.assertEqual(formatted_date, "2023-06-4th")

    def test_count_words(self):
        # Create a test file with content
        with open(self.file_path, "w") as file:
            file.write("This is a test file.")

        # Count the words in the test file
        word_count = count_words(self.file_path)

        # Assert the word count
        self.assertEqual(word_count, 5)


if __name__ == "__main__":
    unittest.main()
