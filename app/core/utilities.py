import copy
import datetime
import logging
import os
import sys
from pathlib import Path

import pytz
from colorama import Fore, Style
from pydantic import FilePath

# specify colors for different logging levels
LOG_COLORS = {
    # logging.DEBUG: Fore.WHITE,
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    # logging.CRITICAL: Fore.RED,
}
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
TEST_DIR = PROJECT_ROOT / "app" / "tests"
EPISODE_TEMPLATE_DIR = PROJECT_ROOT / "app" / "web" / "_pages" / "episodes"
IMAGE_DIR = PROJECT_ROOT / "app" / "web" / "img"
DATABASE_URL = os.getenv("DATABASE_URL")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION_NAME = os.getenv("AWS_REGION_NAME")


class ColourFormatter(logging.Formatter):
    """Display the severity of the log using unique colours
    Credits:
        https://uran198.github.io/en/python/2016/07/12/colorful-python-logging.html
    """

    def format(self, record, *args, **kwargs):
        """
        if the corresponding logger has children, they may receive modified
        record, so we want to keep it intact
        """
        new_record = copy.copy(record)
        if new_record.levelno in LOG_COLORS:
            # we want levelname to be in different color, so let's modify it
            new_record.levelname = "{color_begin}{level}{color_end}".format(
                level=new_record.levelname,
                color_begin=LOG_COLORS[new_record.levelno],
                color_end=Style.RESET_ALL,
            )
        # now we can let standart formatting take care of the rest
        return super(ColourFormatter, self).format(new_record, *args, **kwargs)


def configure_logging():
    """Logging configuration for the project"""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # we want to display levelname, asctime and message
    formatter = ColourFormatter("%(levelname)-12s: %(asctime)-8s %(message)s", datefmt="%d-%b-%y %H:%M:%S")

    # this handler will write to sys.stdout by default
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    # adding handler to our logger
    logger.addHandler(handler)


def delete_file(file_path: str):
    """Delete a file"""
    try:
        os.remove(file_path)
        logging.info(f"File '{file_path}' deleted successfully.")
    except OSError as e:
        logging.error(f"Error occurred while deleting file '{file_path}': {e}")


def format_duration(seconds: int):
    """Format the duration in seconds to a human readable string"""
    minutes, seconds = divmod(seconds, 60)
    duration_string = ""

    if minutes > 0:
        duration_string += f"{minutes} {'minute' if minutes == 1 else 'minutes'}"

    if seconds > 0:
        if duration_string:
            duration_string += ", "

        duration_string += f"{seconds} {'second' if seconds == 1 else 'seconds'}"

    return duration_string


def words_per_minute(duration: int, word_count: int):
    if duration == 0:
        return "0 words per minute"  # Avoid division by zero
    duration_minutes = duration / 60
    rate = word_count / duration_minutes
    rate_int = int(round(rate))  # Convert rate to nearest integer
    return f"{rate_int} words per minute"


def convert_seconds_to_mmss(duration: int):
    minutes, seconds = divmod(duration, 60)
    return "{:02d}:{:02d}".format(minutes, seconds)


def format_filesize(filesize: int):
    """Format the file size in bytes to a human readable string"""
    units = ["B", "KB", "MB", "GB", "TB"]

    # Iterate through units until the file size is smaller than 1024
    for unit in units:
        if filesize < 1024:
            return f"{filesize:.2f} {unit}"
        filesize /= 1024

    # If the file size is larger than the largest unit (TB), return in that unit
    return f"{filesize:.2f} {units[-1]}"


def is_valid_date(datestring: str) -> bool:
    try:
        if datestring != datetime.strptime(datestring, "%Y-%m-%d").strftime("%Y-%m-%d"):
            raise ValueError("Incorrect date format, should be YYYY-MM-DD")
        return True
    except ValueError:
        return False


def suffix(d):
    return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")


def custom_strftime(format, t):
    return t.strftime(format).replace("{S}", str(t.day) + suffix(t.day))


def count_words(filename: FilePath) -> int:
    """Count the number of words in a file"""
    with open(filename, "r") as file:
        content = file.read()
        word_count = len(content.split())
    return word_count


# https://docs.aws.amazon.com/polly/latest/dg/ph-table-english-za.html
podcast_host = "Ayanda"
lingo = "en-ZA"
engine = "neural"

timezone = pytz.timezone("Africa/Lusaka")
today = datetime.datetime.now(timezone).date()

today_iso_fmt = today.isoformat()
today_human_readable = custom_strftime("%A, %B {S}, %Y", today)
podcast_start_date = datetime.date(2023, 6, 1)
