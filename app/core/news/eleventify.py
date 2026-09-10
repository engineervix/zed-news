import json
import logging
import os
from datetime import datetime, timedelta, timezone

import dspy
import pytz
from jinja2 import Environment, PackageLoader, select_autoescape
from together import Together

from app.core.summarization.eleventify import generate_digest_description
from app.core.utilities import DATA_DIR, is_backfill, today, today_human_readable, today_iso_fmt

env = Environment(
    loader=PackageLoader("app", "core/news/template"),
    autoescape=select_autoescape(["html"]),
)
base_template = env.get_template("digest.njk.jinja")
dist_file = f"app/web/_pages/news/{today_iso_fmt}.njk"

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
DESCRIPTION_MODEL = "Qwen/Qwen3.5-9B"

client = Together(api_key=TOGETHER_API_KEY)
DESCRIPTION_LM = dspy.LM(
    f"together_ai/{DESCRIPTION_MODEL}",
    api_key=TOGETHER_API_KEY,
    max_tokens=400,
    reasoning={"enabled": False},
)

digest_metadata_file = f"{DATA_DIR}/{today_iso_fmt}/{today_iso_fmt}_digest.json"

logger = logging.getLogger(__name__)


def create_digest_description(content: str, date: str) -> str:
    """
    Using a DSPy module, create a brief description for the news digest.

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

    try:
        with dspy.context(lm=DESCRIPTION_LM):
            result = generate_digest_description(content).strip()

        logger.info(f"result={result!r}")

        if not result:
            logger.error("Digest description is empty")
            return fallback

        return result

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


def render_jinja_template() -> None:
    """Render the Jinja template for a daily digest.

    Uses today's real date, unless backfilling a past date (is_backfill),
    in which case the page's date/permalink are keyed to that target date.
    """
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
    LSK = pytz.timezone("Africa/Lusaka")
    if is_backfill:
        # Use the target date at midnight rather than the real run time, so the
        # rendered page's date/permalink match the backfilled day, not today.
        digest_dt = LSK.localize(datetime(today.year, today.month, today.day))
    else:
        digest_dt = (datetime.now(timezone.utc) + timedelta(minutes=5)).astimezone(LSK)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(dist_file), exist_ok=True)

    # Render template
    with open(dist_file, "w") as f:
        f.write(
            base_template.render(
                {
                    "title": today_human_readable,
                    "description": digest_description,
                    "date": digest_dt.isoformat(),
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
