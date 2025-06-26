#!/usr/bin/env python

"""post.py

post to social media
"""

__version__ = "1.1.0"

import logging
import os
import pathlib
import random
import sys
from datetime import datetime

import facebook
import requests
from dotenv import load_dotenv
from together import Together

from app.core.utilities import (
    ASSETS_DIR,  # noqa: F401
    DATA_DIR,
    configure_logging,
    timezone,
    today_human_readable,
    today_iso_fmt,
)

PROJECT_ROOT = pathlib.Path(__file__).parents[3]

logger = logging.getLogger(__name__)
load_dotenv(dotenv_path=f"{PROJECT_ROOT}/.env")

# --- Configuration ---
HEALTHCHECKS_PING_URL = os.getenv("HEALTHCHECKS_FACEBOOK_PING_URL")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# --- Initialize Clients ---
client = Together(api_key=TOGETHER_API_KEY)
try:
    graph = facebook.GraphAPI(access_token=FACEBOOK_ACCESS_TOKEN)
except Exception as e:
    logger.error(f"Failed to initialize Facebook GraphAPI: {e}")
    graph = None

# --- File Paths ---
digest_file_path = f"{DATA_DIR}/{today_iso_fmt}/{today_iso_fmt}_digest.json"
digest_url = f"https://zednews.pages.dev/news/{today_iso_fmt}/"
IMAGES_DIR = f"{ASSETS_DIR}/images/promotional"


def get_digest_content() -> str:
    """Get the news digest content from the JSON file."""
    try:
        with open(digest_file_path, "r") as f:
            # Note: The content is nested under the 'content' key
            return f.read()
    except FileNotFoundError:
        logger.error(f"Digest file not found at {digest_file_path}")
        return ""


def create_facebook_post_text(content: str) -> str:
    """Create a Facebook post using Together AI's Inference API."""
    now = datetime.now(timezone).strftime("%I:%M%p")
    system_prompt = (
        f"The time is {now}. You are a social media marketing expert for Zed News, a news digest service for Zambia. "
        "Your task is to create a short, engaging Facebook post based on today's news digest. "
        "The post should:\n"
        "- Start with a warm, friendly, Zambian greeting\n"
        "- Highlight 2-3 of the most interesting or impactful stories.\n"
        "- Use bullet points and relevant emojis to make it scannable.\n"
        "- Maintain a professional yet friendly tone.\n"
        "- End with a clear call to action, encouraging people to read the full digest with a link."
        "- Use appropriate hashtags related to the news and Zambia.\n"
    )
    user_prompt = f"Create a Facebook post for {today_human_readable} based on the following news digest:\n\n{content}\n\nInclude this link at the end: {digest_url}"

    try:
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.75,
            max_tokens=1024,
        )
        post_text = completion.choices[0].message.content
        logger.info(f"Generated Facebook post text:\n{post_text}")
        return post_text
    except Exception as e:
        logger.error(f"Failed to generate Facebook post text: {e}")
        return ""


def get_daily_image(path: str) -> str:
    """
    Get the image for the current day of the week.
    Falls back to a random image if the day-specific image is not found.
    """
    try:
        if not os.path.exists(path):
            raise FileNotFoundError

        today_name = datetime.now().strftime("%A").lower()
        daily_image_path = os.path.join(path, f"{today_name}.jpg")

        if os.path.exists(daily_image_path):
            logger.info(f"Found image for today: {daily_image_path}")
            return daily_image_path

        # Fallback to a random image
        logger.warning(f"No image found for {today_name}. Falling back to a random image.")
        image_files = [f for f in os.listdir(path) if f.endswith((".jpg", ".png"))]
        return os.path.join(path, random.choice(image_files)) if image_files else ""

    except FileNotFoundError:
        logger.error(f"Image directory not found: {path}")
        return ""
    except Exception as e:
        logger.error(f"An unexpected error occurred while getting an image: {e}")
        return ""


def post_to_facebook(text: str, image_path: str):
    """Post a photo with a caption to Facebook."""
    if not all([graph, FACEBOOK_PAGE_ID, text, image_path]):
        logger.error("Missing necessary data for Facebook post. Aborting.")
        if HEALTHCHECKS_PING_URL:
            requests.get(f"{HEALTHCHECKS_PING_URL}/fail", timeout=10)
        return

    logger.info(f"Posting to Facebook page {FACEBOOK_PAGE_ID}...")
    try:
        with open(image_path, "rb") as image_file:
            graph.put_photo(image=image_file, message=text, page_id=FACEBOOK_PAGE_ID)
        logger.info("Successfully posted to Facebook.")
        if HEALTHCHECKS_PING_URL:
            requests.get(HEALTHCHECKS_PING_URL, timeout=10)
    except facebook.GraphAPIError as e:
        logger.error(f"Facebook API Error: {e}")
        if HEALTHCHECKS_PING_URL:
            requests.get(f"{HEALTHCHECKS_PING_URL}/fail", timeout=10)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        if HEALTHCHECKS_PING_URL:
            requests.get(f"{HEALTHCHECKS_PING_URL}/fail", timeout=10)


def main():
    """Main function to generate and post the daily digest to Facebook."""
    configure_logging()
    os.chdir(PROJECT_ROOT)

    digest_content = get_digest_content()
    if not digest_content:
        logger.error("No digest content found. Exiting.")
        sys.exit(1)

    post_text = create_facebook_post_text(digest_content)
    if not post_text:
        logger.error("Failed to generate post text. Exiting.")
        sys.exit(1)

    image_to_post = get_daily_image(IMAGES_DIR)
    if not image_to_post:
        logger.warning("No promotional image found. Posting without an image is not supported.")
        # Do we wanna post text-only or fail?
        # For now, we fail.
        sys.exit(1)

    post_to_facebook(post_text, image_to_post)


if __name__ == "__main__":
    main()
