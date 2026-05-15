import json
import logging
import os
from datetime import datetime, timedelta, timezone

import pytz
from jinja2 import Environment, PackageLoader, select_autoescape
from together import Together

from app.core.utilities import DATA_DIR, today_human_readable, today_iso_fmt

env = Environment(
    loader=PackageLoader("app", "core/news/template"),
    autoescape=select_autoescape(["html"]),
)
base_template = env.get_template("digest.njk.jinja")
dist_file = f"app/web/_pages/news/{today_iso_fmt}.njk"

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
DESCRIPTION_MODEL = "Qwen/Qwen3-235B-A22B-Instruct-2507-tput"

client = Together(api_key=TOGETHER_API_KEY)

digest_metadata_file = f"{DATA_DIR}/{today_iso_fmt}/{today_iso_fmt}_digest.json"

logger = logging.getLogger(__name__)


def create_digest_description(content: str, date: str) -> str:
    """
    Using Together AI's Gemma 4, create a brief description for the news digest.

    Args:
        content: The digest content to summarize
        date: The date of the digest

    Returns:
        str: The generated description or fallback text if generation fails
    """
    fallback = f"News digest for {date} covering the latest developments in Zambian news."

    if not TOGETHER_API_KEY:
        logger.warning("TOGETHER_API_KEY not set, using fallback description")
        return fallback

    prompt = f"""Given the daily news digest below, write a very brief description (1-2 sentences) that captures the main themes and most significant stories of the day. Focus on what readers will find most valuable.

Digest Content:
{content}"""

    try:
        completion = client.chat.completions.create(
            model=DESCRIPTION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            reasoning={"enabled": False},
        )

        choice = completion.choices[0]
        finish_reason = choice.finish_reason
        result = (choice.message.content or "").strip()

        logger.info(f"finish_reason={finish_reason} result={result!r}")

        if not result:
            logger.error(f"Digest description is empty (finish_reason={finish_reason})")
            return fallback

        result = result.replace("```", "")
        first_line = result.splitlines()[0].lower() if result.splitlines() else ""
        unwanted = ["description:", "here's", "here is", "sure"]

        if any(string in first_line for string in unwanted):
            result = "\n".join(result.split("\n")[1:])
            if result.strip() == "":
                logger.warning("Digest description is empty after removing unwanted text")
                return fallback

        return result.replace("\n", " ")

    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"Error generating digest description ({error_type}): {str(e)}")
        return fallback


def get_digest_metadata() -> dict:
    """Load the digest metadata from JSON file"""
    try:
        with open(digest_metadata_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Digest metadata file not found: {digest_metadata_file}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in digest metadata file: {digest_metadata_file}")
        return {}


def render_jinja_template():
    """Render the Jinja template for a daily digest"""
    logger.info("Rendering Jinja template for daily digest...")

    # Load digest metadata
    digest_data = get_digest_metadata()

    if not digest_data:
        logger.error("No digest metadata available, cannot render template")
        return

    # Create digest description
    digest_description = create_digest_description(digest_data.get("content", ""), today_human_readable)

    # Prepare sources list and articles from digest data (no database query needed)
    sources = digest_data.get("sources", [])
    digest_articles = digest_data.get("articles", [])

    # Setup timezone
    utc_dt = datetime.now(timezone.utc) + timedelta(minutes=5)
    LSK = pytz.timezone("Africa/Lusaka")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(dist_file), exist_ok=True)

    # Render template
    with open(dist_file, "w") as f:
        f.write(
            base_template.render(
                {
                    "title": today_human_readable,
                    "description": digest_description,
                    "date": utc_dt.astimezone(LSK).isoformat(),
                    "digest_content": digest_data.get("content", ""),
                    "total_articles": digest_data.get("total_articles", len(digest_articles)),
                    "num_sources": len(sources),
                    "sources": sources,
                    "articles": [
                        {
                            "source": article["source"],
                            "url": article["url"],
                            "title": article["title"],
                        }
                        for article in digest_articles
                    ],
                    "generated_at": digest_data.get("generated_at", ""),
                }
            ),
        )

    logger.info(f"Daily digest template rendered successfully: {dist_file}")
