#!/usr/bin/env python

"""post.py

post to social media
"""

__version__ = "1.1.0"

import argparse
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

# --- Model Configuration ---
TEXT_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
# IMAGE_MODEL = "imagen-3.0-generate-002"
IMAGE_MODEL = "imagen-4.0-generate-preview-06-06"
IMAGE_CONCEPT_TEMP = 0.8
FACEBOOK_POST_TEMP = 0.7

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
            return f.read()
    except FileNotFoundError:
        logger.error(f"Digest file not found at {digest_file_path}")
        return ""


def get_image_prompt_concept(content: str) -> str:
    """Generate a creative image prompt concept from the digest content using an LLM."""
    if not content:
        logger.warning("No content provided to generate image prompt concept.")
        return ""

    if not TOGETHER_API_KEY:
        logger.warning("TOGETHER_API_KEY not set, skipping image prompt concept generation.")
        return ""

    system_prompt = (
        "You are a Creative Director for Zed News, a Zambian news outlet. "
        "Your goal is to create a concept for a promotional image that captures the essence of today's news digest. "
        "The image should be symbolic, professional, and optimistic, reflecting themes of innovation, development, "
        "community, and national pride in Zambia. Read the provided news digest, identify the most visually "
        "compelling or impactful story, and describe a single, clear photographic scene.\n\n"
        "GUIDELINES:\n"
        "- Read the entire digest to understand the key stories.\n"
        "- Select the ONE story that is most visually interesting or emotionally resonant.\n"
        "- Describe a photograph that represents this story symbolically. Do NOT be literal.\n"
        "- Depict Zambians as professionals, innovators, community members, and families.\n"
        "- The tone must be professional, hopeful, and forward-looking.\n"
        "- AVOID: Clichés, poverty imagery, political figures, direct depictions of negative events (e.g., accidents, crime). "
        "If the news is negative, find a positive or neutral angle (e.g., for a cholera outbreak, show a scientist in a lab).\n"
        "- OUTPUT FORMAT: Respond with ONLY the concise, one-sentence description of the photographic scene. Do not add any other text."
    )

    user_prompt = f"Here is today's news digest for Zambia. Generate a creative photo concept based on it:\n\n{content}"

    try:
        completion = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=IMAGE_CONCEPT_TEMP,
            max_tokens=150,
        )
        concept = completion.choices[0].message.content.strip()
        logger.info(f"Generated image prompt concept: {concept}")
        return concept
    except Exception as e:
        logger.error(f"Failed to generate image prompt concept: {e}")
        return ""


def build_final_image_prompt(concept: str) -> str:
    """Build the final Imagen prompt by combining the creative concept with technical and stylistic requirements."""
    prompt = (
        "Create a high-quality, professional photograph with absolutely no overlaid text, logos, or graphics. "
        f"{concept}. "
        "High-end photography style, sharp focus on the subject, professional lighting, "
        "modern African professional aesthetic, avoid rural or poverty imagery, "
        "emphasize contemporary urban development and prosperity, "
        "4K HDR quality, taken by a professional photographer, "
        "no text overlays, watermarks, graphic elements, frames, borders, or captions added to the image."
    )

    return prompt


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

    # Generate a creative concept and build the final prompt
    concept = get_image_prompt_concept(content)
    if not concept:
        logger.error("Failed to generate image prompt concept.")
        return ""
    prompt = build_final_image_prompt(concept)

    logger.info(f"Generating image with concept: {concept}")

    try:
        client_genai = genai.Client(api_key=GOOGLE_API_KEY)

        try:
            config_obj = types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="1:1",
            )
        except TypeError as e:
            logger.warning(f"GenerateImagesConfig missing fields (aspect_ratio): {e}. Falling back to minimal config.")
            config_obj = types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
            )

        response = client_genai.models.generate_images(
            model=IMAGE_MODEL,
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

        logger.info(f"Generated promotional image at {output_path} (concept: {concept})")
        return output_path
    except Exception as e:
        logger.error(f"Failed to generate promotional image: {e}")
        return ""


def create_facebook_post_text(content: str) -> str:
    """Create a Facebook post using Together AI's Inference API."""
    now = datetime.now(timezone)
    hour = now.hour

    # Determine time of day for context (but don't mention specific time)
    if 5 <= hour < 12:
        time_context = "morning"
    elif 12 <= hour < 17:
        time_context = "afternoon"
    elif 17 <= hour < 21:
        time_context = "evening"
    else:
        time_context = "night"

    system_prompt = (
        f"You are a patriotic Zambian social media editor for Zed News. Your tone is passionate and engaging. "
        f"It's {time_context} and you're bringing Zambians the day's most important stories. "
        "Adapt your tone naturally to match the content - celebratory for good news, respectful for serious matters, "
        "informative for policy changes, and balanced for mixed content. "
        f"NEVER mention specific times (like 5:45PM) in your post. "
        "CRITICAL: Most readers will NEVER click the link - make this post completely valuable on its own. "
        "FORMATTING RULES - STRICTLY ENFORCE:\n"
        "- Use ONLY plain text with line breaks and emojis\n"
        "- NEVER use markdown syntax (**, *, _, `, #, -, etc.)\n"
        "- NEVER use bullet points (•, -, *, 1., 2., etc.)\n"
        "- NEVER use asterisks for emphasis\n"
        "- NEVER use underscores for emphasis\n"
        "- NEVER use hashtags as headers\n"
        "- Use natural paragraph breaks and emojis for visual structure\n\n"
        "Craft an engaging Facebook post that:\n"
        f"- Starts with a creative, context-aware greeting suitable for the {time_context}\n"
        "- Presents 4-5 key stories in conversational paragraphs (NOT lists or bullet points)\n"
        "- Each story should be 1-2 short sentences explaining WHAT happened and WHY it matters to us as Zambians\n"
        "- Use patriotic and inclusive language (e.g., 'our nation', 'we', 'our fellow citizens')\n"
        "- Use emojis strategically (1 per story max) for visual breaks and emotion\n"
        "- Use line breaks between stories for mobile readability\n"
        "- Include specific numbers/facts that people want to share in WhatsApp groups\n"
        "- Make each story relatable to daily life (jobs, money, safety, family)\n"
        "- End with a creative, engaging call-to-action to spark conversation\n"
        "- Weave in a few relevant hashtags like #Zambia, #ZambianNews, or story-specific ones, but do NOT just list them at the end\n"
        "- Include the link at the very end\n\n"
        "Write for mobile users scrolling fast - make it instantly valuable and shareable. "
        "Vary your language and avoid repetitive phrases. "
        "Remember: NO markdown formatting whatsoever - only plain text, line breaks, and emojis."
    )

    user_prompt = (
        f"Create a Facebook post for {today_human_readable} based on this news digest. "
        "Remember: NO markdown, NO bullet points, NO specific times mentioned - use plain text with line breaks and emojis.\n\n"
        f"DIGEST:\n{content}\n\n"
        f"End with this link: {digest_url}"
    )

    try:
        completion = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=FACEBOOK_POST_TEMP,
            max_tokens=1800,
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


def generate_image_only(content: str) -> str:
    """Generate only the promotional image without posting to Facebook."""
    logger.info("Image-only mode: Generating promotional image...")

    image_path = generate_promotional_image(content)
    if image_path:
        logger.info(f"Image generated successfully: {image_path}")
        print(f"\nImage generated: {image_path}")
        return image_path
    else:
        logger.error("Failed to generate image")
        print("\nFailed to generate image")
        return ""


def generate_text_only(content: str) -> str:
    """Generate only the post text without posting to Facebook."""
    logger.info("Text-only mode: Generating post text...")

    post_text = create_facebook_post_text(content)
    if post_text:
        logger.info("Post text generated successfully")
        print("\nGenerated Facebook post text:")
        print("=" * 60)
        print(post_text)
        print("=" * 60)
        return post_text
    else:
        logger.error("Failed to generate post text")
        print("\nFailed to generate post text")
        return ""


def dry_run_mode(content: str):
    """Generate both text and image but don't post to Facebook."""
    logger.info("Dry-run mode: Generating text and image without posting...")

    print("\nDry run mode - No posting to Facebook")
    print("=" * 50)

    # Generate text
    post_text = create_facebook_post_text(content)
    if post_text:
        print("\nGenerated Facebook post text:")
        print("-" * 40)
        print(post_text)
        print("-" * 40)
    else:
        print("\nFailed to generate post text")

    # Generate image
    image_path = generate_promotional_image(content) or get_daily_image(IMAGES_DIR)
    if image_path:
        print(f"\nImage ready: {image_path}")
    else:
        print("\nNo image available - would post text-only")

    if post_text and image_path:
        print("\nReady to post: Text + Image")
    elif post_text:
        print("\nReady to post: Text only")
    else:
        print("\nNothing ready to post")

    print("\n" + "=" * 50)


def main():
    """Main function to generate and post the daily digest to Facebook."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate and post daily news digest")
    parser.add_argument(
        "--image-only", action="store_true", help="Generate promotional image only, without posting to Facebook"
    )
    parser.add_argument("--text-only", action="store_true", help="Generate post text only, without posting to Facebook")
    parser.add_argument(
        "--dry-run", action="store_true", help="Generate both text and image but don't post to Facebook"
    )
    # Use parse_known_args so tests (or parent processes) passing extra args don't cause SystemExit
    args, _ = parser.parse_known_args()

    configure_logging()
    os.chdir(PROJECT_ROOT)

    digest_content = get_digest_content()
    if not digest_content:
        logger.error("No digest content found. Exiting.")
        sys.exit(1)

    # Check for mutually exclusive flags
    mode_flags = [args.image_only, args.text_only, args.dry_run]
    if sum(mode_flags) > 1:
        logger.error(
            "Cannot use multiple test modes simultaneously. Choose one: --image-only, --text-only, or --dry-run"
        )
        sys.exit(1)

    # Image-only mode
    if args.image_only:
        generate_image_only(digest_content)
        return

    # Text-only mode
    if args.text_only:
        generate_text_only(digest_content)
        return

    # Dry-run mode
    if args.dry_run:
        dry_run_mode(digest_content)
        return

    # Normal posting mode
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
