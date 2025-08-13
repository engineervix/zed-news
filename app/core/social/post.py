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
from google import genai
from google.genai import types
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
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Initialize Clients ---
client = Together(api_key=TOGETHER_API_KEY)
try:
    graph = facebook.GraphAPI(access_token=FACEBOOK_ACCESS_TOKEN)
except Exception as e:
    logger.error(f"Failed to initialize Facebook GraphAPI: {e}")
    graph = None

# --- File Paths ---
digest_file_path = f"{DATA_DIR}/{today_iso_fmt}/{today_iso_fmt}_digest-content.txt"
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


def build_image_prompt_from_digest(content: str) -> str:
    """Derive a concise visual prompt from the digest content.

    Uses Together to pick 2-3 key topics and describe a safe, text-free scene.
    Falls back to a simple heuristic if the model fails.
    """
    base_fallback = (
        "An abstract, modern composition that evokes today's key Zambian news themes, "
        "with subtle national color accents and positive, community-focused energy."
    )

    if not content or not TOGETHER_API_KEY:
        return base_fallback

    try:
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You generate concise visual prompts for an image model. "
                        "Extract 2-3 prominent topics from the user's Zambian news digest and describe a single coherent scene. "
                        "Describe only objects, scenery, colors, mood, and lighting. "
                        "Never mention or imply text, words, letters, numbers, typography, signage, labels, or any logos/brands. "
                        "Return 1 short sentence."
                    ),
                },
                {"role": "user", "content": content},
            ],
            temperature=0.5,
            max_tokens=160,
        )
        prompt = completion.choices[0].message.content or ""
        # Basic sanitation: collapse whitespace, strip
        prompt = " ".join(prompt.split()).strip()
        if not prompt:
            return base_fallback
        return prompt
    except Exception as e:
        logger.error(f"Failed to build image prompt from digest: {e}")
        return base_fallback


def generate_promotional_image(content: str) -> str:
    """Generate a fresh promotional image using Google GenAI and save it locally.

    Returns the absolute file path to the generated image, or an empty string on failure.
    """
    if not GOOGLE_API_KEY:
        logger.warning("GOOGLE_API_KEY is not set. Skipping image generation.")
        return ""

    # Create output directory under DATA_DIR/today/social
    output_dir = os.path.join(DATA_DIR, today_iso_fmt, "social")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "facebook-promotional.jpeg")

    # Build a news-related visual prompt from the digest content
    digest_visual_prompt = build_image_prompt_from_digest(content)
    prompt = (
        "Create a vibrant, friendly promotional image for a daily Zambian news digest. "
        "Use brand-neutral colors and subtle Zambian cultural motifs (patterns or flag colors). "
        "Strictly exclude any text, words, letters, numbers, typographic elements, signage, labels, watermarks, or logos. "
        "Prioritize clarity at social-media thumbnail sizes. "
        f"Scene guidance: {digest_visual_prompt}"
    )

    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        # Negative prompt to steer away from text/logos
        # (see https://cloud.google.com/vertex-ai/generative-ai/docs/image/img-gen-prompt-guide)
        negative_terms = (
            "text, letters, words, numbers, typography, fonts, signage, labels, captions, titles, headlines, "
            "ui, interface, screenshot, watermark, watermarks, logos, trademarks, brand names, Zed News"
        )

        # Try using newer Imagen config fields; fall back if unsupported in current SDK
        try:
            config_obj = types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="1:1",
                negative_prompt=negative_terms,
            )
        except TypeError as e:
            logger.warning(
                f"GenerateImagesConfig missing fields (aspect_ratio/negative_prompt): {e}. Falling back to minimal config."
            )
            config_obj = types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
            )

        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config=config_obj,
        )

        # Validate response and extract bytes safely
        if not response or not getattr(response, "generated_images", None):
            logger.error("Image generation failed: empty response or no images returned.")
            return ""

        image_obj = response.generated_images[0].image if response.generated_images else None
        image_bytes = getattr(image_obj, "image_bytes", None)
        if not image_bytes:
            logger.error("Image generation failed: no image bytes found in response.")
            return ""

        with open(output_path, "wb") as f:
            f.write(image_bytes)

        # Ensure the file was actually written and has content
        try:
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                logger.error("Image generation failed: output file missing or empty.")
                return ""
        except OSError:
            logger.error("Image generation failed: could not validate output file size.")
            return ""

        logger.info(f"Generated promotional image at {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to generate promotional image: {e}")
        return ""


def create_facebook_post_text(content: str) -> str:
    """Create a Facebook post using Together AI's Inference API."""
    now = datetime.now(timezone).strftime("%I:%M%p")
    system_prompt = (
        f"The time is {now}. You are a social media editor for Zed News (a Zambian news digest). "
        "Assume most readers will not click the link, so make the post stand alone and complete while staying concise. "
        "Craft an engaging Facebook post that:\n"
        "- Starts with a warm, friendly greeting and a short one-line summary of the day.\n"
        "- Highlights 3–5 of the most important stories with ultra-brief bullets (1–2 lines each).\n"
        "- For each bullet, include what happened and why it matters in plain language.\n"
        "- Uses tasteful, relevant emojis (max 1 per bullet) to aid scannability.\n"
        "- Keeps a professional, friendly tone suitable for a broad Zambian audience.\n"
        "- Limits hashtags to 2–4 targeted tags at the end (e.g., #Zambia, #News).\n"
        "- Includes the link at the very end, after the hashtags."
    )
    user_prompt = (
        f"Create a Facebook post for {today_human_readable} based on the following news digest. "
        "Make the post self-contained and valuable even if the reader never clicks the link.\n\n"
        f"DIGEST:\n{content}\n\n"
        f"End the post with 2–4 concise hashtags, then the link: {digest_url}"
    )

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


def post_text_only_to_facebook(text: str):
    """Post a text-only update to Facebook when no image is available."""
    if not all([graph, FACEBOOK_PAGE_ID, text]):
        logger.error("Missing necessary data for Facebook text-only post. Aborting.")
        if HEALTHCHECKS_PING_URL:
            requests.get(f"{HEALTHCHECKS_PING_URL}/fail", timeout=10)
        return

    logger.info(f"Posting text-only update to Facebook page {FACEBOOK_PAGE_ID}...")
    try:
        # Post to the page feed with message only
        graph.put_object(parent_object=FACEBOOK_PAGE_ID, connection_name="feed", message=text)
        logger.info("Successfully posted text-only update to Facebook.")
        if HEALTHCHECKS_PING_URL:
            requests.get(HEALTHCHECKS_PING_URL, timeout=10)
    except facebook.GraphAPIError as e:
        logger.error(f"Facebook API Error (text-only): {e}")
        if HEALTHCHECKS_PING_URL:
            requests.get(f"{HEALTHCHECKS_PING_URL}/fail", timeout=10)
    except Exception as e:
        logger.error(f"An unexpected error occurred (text-only): {e}")
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

    # Try generating a fresh image; if unavailable, fallback to curated daily image
    image_to_post = generate_promotional_image(digest_content) or get_daily_image(IMAGES_DIR)
    if not image_to_post:
        logger.warning("No promotional image available. Proceeding with text-only Facebook post.")
        post_text_only_to_facebook(post_text)
        return

    post_to_facebook(post_text, image_to_post)


if __name__ == "__main__":
    main()
