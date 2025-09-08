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

# --- Mood-based Visual Prompts ---
MOOD_VISUAL_PROMPTS = {
    "positive": (
        "Professional person in business attire reading a newspaper. The newspaper should feature generic, unreadable text to avoid showing fake content. "
        "Scene: modern Zambian office or urban setting, bright natural lighting, "
        "contemporary architecture, technology elements like smartphones or tablets nearby, "
        "sophisticated atmosphere, prosperous and forward-looking environment, clean modern aesthetic."
    ),
    "serious": (
        "Thoughtful professional reading a newspaper where the text is generic and not legible. "
        "Scene: modern indoor setting with contemporary furniture, soft natural lighting, "
        "urban Zambian backdrop through windows, sophisticated workspace, "
        "calm professional environment, modern African business context."
    ),
    "dynamic": (
        "Business professional engaging with news content on a tablet and a printed newspaper. The newspaper text must be generic and unreadable. "
        "Scene: dynamic modern office space, bright lighting, contemporary Zambian cityscape visible, "
        "mix of digital and traditional media, progressive workspace with modern technology, "
        "vibrant urban professional setting, forward-thinking atmosphere."
    ),
    "mixed": (
        "Person in smart casual attire reading a newspaper with generic, non-legible text. "
        "Scene: comfortable modern living space or café setting, balanced natural lighting, "
        "contemporary Zambian urban environment, relaxed but professional atmosphere, "
        "modern African lifestyle, mix of traditional and contemporary elements."
    ),
    "economic": (
        "Business professional reviewing a financial newspaper. The text, charts, and headlines must be generic and unreadable to avoid showing fake data. "
        "Scene: modern office environment with computers and financial displays, "
        "contemporary Zambian business district backdrop, professional corporate setting, "
        "emphasis on growth and development, sophisticated business atmosphere with modern technology."
    ),
}


def get_digest_content() -> str:
    """Get the news digest content from the JSON file."""
    try:
        with open(digest_file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Digest file not found at {digest_file_path}")
        return ""


def analyze_digest_mood(content: str, override_mood: str | None = None) -> str:
    """Analyze the overall mood/sentiment of the digest using LLM."""
    if override_mood:
        logger.info(f"Using override mood: {override_mood}")
        return override_mood

    if not content:
        return "mixed"

    # If Together API key isn't configured, skip external call to keep things fast/testable
    if not TOGETHER_API_KEY:
        return "mixed"

    system_prompt = (
        "You are a sentiment analyzer for news content. Analyze the overall mood/tone "
        "of the provided news digest and return ONE of these categories:\n"
        "- 'positive': Predominantly good news (economic growth, achievements, progress)\n"
        "- 'serious': Predominantly serious/somber news (deaths, accidents, crises)\n"
        "- 'dynamic': Focus on policy changes, developments, government actions\n"
        "- 'economic': Primarily economic/financial news\n"
        "- 'mixed': Balanced mix of different types of news\n\n"
        "Consider the prominence and emotional weight of stories. Respond with ONLY the category word."
    )

    user_prompt = f"Analyze the mood/sentiment of this Zambian news digest and classify it:\n\n{content}"

    try:
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=50,
        )

        mood = completion.choices[0].message.content.strip().lower()

        # Validate the response
        if mood in MOOD_VISUAL_PROMPTS:
            logger.info(f"Detected digest mood: {mood}")
            return mood
        else:
            logger.warning(f"Invalid mood response '{mood}', defaulting to 'mixed'")
            return "mixed"

    except Exception as e:
        logger.error(f"Failed to analyze digest mood: {e}")
        return "mixed"


def build_image_prompt_from_mood(mood: str) -> str:
    """Build an Imagen prompt based on the analyzed mood."""
    base_visual = MOOD_VISUAL_PROMPTS.get(mood, MOOD_VISUAL_PROMPTS["mixed"])

    # Core prompt structure that ensures readable newspaper content
    prompt = (
        "Create a high-quality, professional photograph with absolutely no overlaid text, logos, or graphics. "
        f"{base_visual}. "
        "The newspaper should show realistic printed text, headlines, and articles - make it look like a real newspaper with actual content. "
        "High-end photography style, sharp focus, professional lighting, "
        "modern African professional aesthetic, avoid rural or poverty imagery, "
        "emphasize contemporary urban development and prosperity, "
        "no text overlays, watermarks, or graphic elements added to the image."
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

    # Analyze mood and build appropriate visual prompt
    mood = analyze_digest_mood(content)
    prompt = build_image_prompt_from_mood(mood)

    logger.info(f"Generating image with mood '{mood}' and prompt: {prompt[:100]}...")

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
            # model="imagen-3.0-generate-002",
            model="imagen-4.0-generate-preview-06-06",
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

        logger.info(f"Generated promotional image at {output_path} (mood: {mood})")
        return output_path
    except Exception as e:
        logger.error(f"Failed to generate promotional image: {e}")
        return ""


def create_facebook_post_text(content: str, mood_override: str | None = None) -> str:
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

    # Keep text generation deterministic for tests; avoid extra LLM call here
    mood = mood_override if mood_override in MOOD_VISUAL_PROMPTS else "mixed"

    # Varied greeting styles based on time context
    greeting_variations = {
        "morning": [
            "Good morning, Zambia! 🌅",
            "Rise and shine! ☀️",
            "Morning update for Zambia:",
            "Starting the day with important news:",
            "What's happening this morning in Zambia:",
        ],
        "afternoon": [
            "Good afternoon! 🌞",
            "Midday news update:",
            "Here's what's happening this afternoon:",
            "Your afternoon news briefing:",
            "Checking in with today's developments:",
        ],
        "evening": [
            "Good evening, Zambia! 🌆",
            "Evening news wrap-up:",
            "As the day winds down, here's what happened:",
            "Your evening update:",
            "End-of-day news summary:",
        ],
        "night": [
            "Late night update:",
            "Before you rest, here's today's news:",
            "Tonight's summary:",
            "As the day ends, here's what mattered:",
            "Your late evening update:",
        ],
    }

    # Varied call-to-action endings
    call_to_action_variations = [
        "What story resonates with you?",
        "Which development matters most to your family?",
        "What's your take on today's news?",
        "Which story will you be discussing tomorrow?",
        "What caught your attention today?",
        "Which development affects you most?",
        "What story are you sharing with friends?",
        "Which news impacts your community?",
        "What's most important to you here?",
        "Which story deserves more attention?",
    ]

    # Mood-specific context additions
    mood_contexts = {
        "positive": "celebrating progress and achievements",
        "serious": "focusing on important developments",
        "dynamic": "covering major changes and updates",
        "economic": "examining business and financial news",
        "mixed": "bringing you diverse stories",
    }

    # Randomly select greeting and call-to-action
    selected_greeting = random.choice(greeting_variations[time_context])
    selected_cta = random.choice(call_to_action_variations)
    mood_context = mood_contexts.get(mood, mood_contexts["mixed"])

    system_prompt = (
        f"You are a social media editor for Zed News (a Zambian news digest). "
        f"It's {time_context} and you're {mood_context}. "
        f"NEVER mention specific times (like 5:45PM) in your post. "
        "CRITICAL: Most readers will NEVER click the link - make this post completely valuable on its own. "
        "Facebook posts do NOT support markdown - use plain text with strategic formatting.\n\n"
        "Craft an engaging Facebook post that:\n"
        f"- Starts with this greeting: '{selected_greeting}'\n"
        "- Presents 4-5 key stories in conversational paragraphs (NOT bullet points)\n"
        "- Each story should be 1-2 short sentences explaining WHAT happened and WHY it matters to ordinary Zambians\n"
        "- Use emojis strategically (1 per story max) for visual breaks and emotion\n"
        "- Use line breaks between stories for mobile readability\n"
        "- Include specific numbers/facts that people want to share in WhatsApp groups\n"
        "- Make each story relatable to daily life (jobs, money, safety, family)\n"
        f"- End with this call-to-action: '{selected_cta}'\n"
        "- Add 2-3 hashtags: #Zambia #ZedNews and one relevant tag\n"
        "- Include the link at the very end\n\n"
        "Write for mobile users scrolling fast - make it instantly valuable and shareable. "
        "Vary your language and avoid repetitive phrases."
    )

    user_prompt = (
        f"Create a Facebook post for {today_human_readable} based on this news digest. "
        "Remember: NO markdown, NO bullet points, NO specific times mentioned - use plain text with line breaks and emojis.\n\n"
        f"DIGEST:\n{content}\n\n"
        f"End with hashtags, then this link: {digest_url}"
    )

    try:
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=1200,
        )
        post_text = completion.choices[0].message.content
        logger.info(f"Generated Facebook post text (mood: {mood}):\n{post_text}")
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


def generate_image_only(content: str, override_mood: str | None = None) -> str:
    """Generate only the promotional image without posting to Facebook."""
    logger.info("Image-only mode: Generating promotional image...")

    # Analyze mood (with potential override)
    mood = analyze_digest_mood(content, override_mood)

    image_path = generate_promotional_image(content)
    if image_path:
        logger.info(f"Image generated successfully: {image_path}")
        print(f"\n  Image generated: {image_path}")
        print(f" Detected mood: {mood}")
        return image_path
    else:
        logger.error("Failed to generate image")
        print("\nFailed to generate image")
        return ""


def main():
    """Main function to generate and post the daily digest to Facebook."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate and post daily news digest")
    parser.add_argument(
        "--image-only", action="store_true", help="Generate promotional image only, without posting to Facebook"
    )
    parser.add_argument(
        "--mood",
        choices=list(MOOD_VISUAL_PROMPTS.keys()),
        help="Override mood detection with specific mood for image generation",
    )
    # Use parse_known_args so tests (or parent processes) passing extra args don't cause SystemExit
    args, _ = parser.parse_known_args()

    configure_logging()
    os.chdir(PROJECT_ROOT)

    digest_content = get_digest_content()
    if not digest_content:
        logger.error("No digest content found. Exiting.")
        sys.exit(1)

    # Image-only mode
    if args.image_only:
        generate_image_only(digest_content, args.mood)
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
