import os
import unittest
from datetime import date, datetime
from unittest.mock import patch

import pytz

from app.core.utilities import custom_strftime, resolve_target_date, suffix


class TestUtilities(unittest.TestCase):
    def setUp(self):
        self.file_path = "test_file.txt"

    def tearDown(self):
        # Clean up the test file after each test
        try:
            os.remove(self.file_path)
        except FileNotFoundError:
            pass

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


class TestResolveTargetDate(unittest.TestCase):
    def setUp(self):
        self.tz = pytz.timezone("Africa/Lusaka")

    def test_no_override_returns_actual_today(self):
        self.assertEqual(resolve_target_date(None, self.tz), datetime.now(self.tz).date())

    def test_override_returns_that_date(self):
        self.assertEqual(resolve_target_date("2026-09-09", self.tz), date(2026, 9, 9))

    def test_malformed_override_raises(self):
        with self.assertRaises(ValueError):
            resolve_target_date("09-09-2026", self.tz)


if __name__ == "__main__":
    unittest.main()
