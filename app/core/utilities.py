import copy
import datetime
import logging
import os
import re
import sys
from pathlib import Path

import pytz
from colorama import Fore, Style
from dotenv import load_dotenv

load_dotenv()

# specify colors for different logging levels
LOG_COLORS = {
    # logging.DEBUG: Fore.WHITE,
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    # logging.CRITICAL: Fore.RED,
}
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")


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


def remove_think_tags(text: str) -> str:
    """Strip <think>...</think> blocks some models (e.g. DeepSeek) may leak into content."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)


def truncate(text: str, max_length: int) -> str:
    """Clip `text` to `max_length` characters, appending an ellipsis if it was cut."""
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "…"


def suffix(d):
    return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")


def custom_strftime(format, t):
    return t.strftime(format).replace("{S}", str(t.day) + suffix(t.day))


def resolve_target_date(override: str | None, tz: pytz.BaseTzInfo) -> datetime.date:
    """The digest's target date: ZED_NEWS_DATE (ISO format, e.g. 2026-09-09) if set, else today in tz."""
    if override:
        return datetime.date.fromisoformat(override)
    return datetime.datetime.now(tz).date()


timezone = pytz.timezone("Africa/Lusaka")
today = resolve_target_date(os.getenv("ZED_NEWS_DATE"), timezone)
is_backfill = today != resolve_target_date(None, timezone)

today_iso_fmt = today.isoformat()
today_human_readable = custom_strftime("%A, %B {S}, %Y", today)
