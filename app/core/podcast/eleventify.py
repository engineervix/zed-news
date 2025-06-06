import json
import logging
import os
from datetime import datetime, timedelta, timezone

import pytz
from babel import Locale
from google import genai
from jinja2 import Environment, PackageLoader, select_autoescape

from app.core.db.models import Article
from app.core.utilities import DATA_DIR, format_duration, lingo, today, today_human_readable, today_iso_fmt

env = Environment(
    loader=PackageLoader("app", "core/podcast/template"),
    autoescape=select_autoescape(["html"]),
)
base_template = env.get_template("digest.njk.jinja")
dist_file = f"src/news/{today_iso_fmt}.njk"

# Google
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1alpha"})

digest_metadata_file = f"{DATA_DIR}/{today_iso_fmt}/{today_iso_fmt}_digest.json"

logger = logging.getLogger(__name__)


def create_digest_description(content: str, date: str) -> str:
    """
    Using Google's Gemini API, create a brief description for the daily digest.

    Args:
        content: The digest content to summarize
        date: The date of the digest

    Returns:
        str: The generated description or fallback text if generation fails
    """
    fallback = f"Daily news digest for {date} covering the latest developments in Zambian news."

    try:
        prompt = f"""Given the daily news digest below, write a very brief description (1-2 sentences) that captures the main themes and most significant stories of the day. Focus on what readers will find most valuable.

Digest Content:
{content}"""

        # Create request for Gemini
        model = "gemini-2.0-flash"
        response = gemini_client.models.generate_content(
            model=model,
            contents=prompt,
        )

        logger.info(response)

        if result := response.text.strip():
            result = result.replace("```", "")  # Remove triple backticks
            first_line = result.splitlines()[0].lower() if result.splitlines() else ""
            unwanted = ["description:", "here's", "here is", "sure"]

            if any(string in first_line for string in unwanted):
                # Remove the first line from result
                result = "\n".join(result.split("\n")[1:])
                if result.strip() == "":
                    logger.warning("Digest description is empty after removing unwanted text")
                    return fallback

            return result.replace("\n", " ")  # Remove newlines and join as single line
        else:
            logger.error("Digest description is empty")
            return fallback

    except Exception as e:
        # Catch all exceptions to ensure the function never fails completely
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


def render_jinja_template(processing_time: int):
    """Render the Jinja template for a daily digest"""
    logging.info("Rendering Jinja template for daily digest...")

    # Load digest metadata
    digest_data = get_digest_metadata()

    if not digest_data:
        logging.error("No digest metadata available, cannot render template")
        return

    # Get articles for today
    articles = Article.select().where(Article.date == today)

    # Create digest description
    digest_description = create_digest_description(digest_data.get("content", ""), today_human_readable)

    # Prepare sources list
    sources = digest_data.get("sources", [])

    # Setup timezone
    lc = Locale.parse(lingo.replace("-", "_"))
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
                    "locale_id": lingo,
                    "locale_name": lc.display_name,
                    "processing_time": format_duration(processing_time),
                    "total_articles": digest_data.get("total_articles", len(articles)),
                    "num_sources": len(sources),
                    "sources": sources,
                    "articles": [
                        {
                            "source": article.source,
                            "url": article.url,
                            "title": f'"{article.title}"',
                            "summary": article.summary,
                        }
                        for article in articles
                    ],
                    "generated_at": digest_data.get("generated_at", ""),
                }
            ),
        )

    logging.info(f"Daily digest template rendered successfully: {dist_file}")


def cleanup_old_templates(days_to_keep: int = 30):
    """Remove old digest template files to prevent accumulation"""
    news_dir = "src/news"
    if not os.path.exists(news_dir):
        return

    cutoff_date = datetime.now() - timedelta(days=days_to_keep)

    for filename in os.listdir(news_dir):
        if filename.endswith(".njk") and len(filename) == 14:  # YYYY-MM-DD.njk format
            try:
                file_date = datetime.strptime(filename[:10], "%Y-%m-%d")
                if file_date < cutoff_date:
                    file_path = os.path.join(news_dir, filename)
                    os.remove(file_path)
                    logging.info(f"Removed old digest template: {filename}")
            except ValueError:
                # Skip files that don't match expected date format
                continue
