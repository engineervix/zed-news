import logging
import os
from datetime import datetime, timedelta, timezone

import pytz
from babel import Locale
from google import genai
from jinja2 import Environment, PackageLoader, select_autoescape

# from num2words import num2words
from app.core.db.models import Article, Episode, Mp3
from app.core.utilities import (
    DATA_DIR,
    EPISODE_TEMPLATE_DIR,
    convert_seconds_to_mmss,
    format_duration,
    format_filesize,
    lingo,
    podcast_host,
    today,
    today_human_readable,
    today_iso_fmt,
    words_per_minute,
)

env = Environment(
    loader=PackageLoader("app", "core/podcast/template"),
    autoescape=select_autoescape(["html"]),
)
base_template = env.get_template("episode.njk.jinja")
dist_file = f"{EPISODE_TEMPLATE_DIR}/{today_iso_fmt}.njk"

# Google
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1alpha"})

transcript = f"{DATA_DIR}/{today_iso_fmt}_podcast-content.txt"

logger = logging.getLogger(__name__)


def create_episode_summary(content: str, episode: str) -> str:
    """
    Using Google's Gemini API, create a summary to use as episode description.

    Args:
        content: The content to summarize
        episode: The episode number/identifier

    Returns:
        str: The generated summary or fallback text if generation fails
    """
    fallback = f"This is episode {episode} of the Zed News Podcast."

    try:
        prompt = f"""Given the details of today's episode below, write a very brief summary to use as a description for the media file. Your summary should be a single paragraph, not exceeding 2 sentences. Focus on the most significant news stories and their impact.

Content:
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
            unwanted = ["summary:", "here's", "here is", "sure"]

            if any(string in first_line for string in unwanted):
                # Remove the first line from result
                result = "\n".join(result.split("\n")[1:])
                if result.strip() == "":
                    logger.warning("Podcast episode summary is empty after removing unwanted text")
                    return fallback

            return result.replace("\n", "")  # Remove newlines
        else:
            logger.error("Podcast episode summary is empty")
            return fallback

    except Exception as e:
        # Catch all exceptions to ensure the function never fails completely
        error_type = type(e).__name__
        logger.error(f"Error generating episode summary ({error_type}): {str(e)}")
        return fallback


def get_content() -> str:
    """Get the headlines"""
    with open(transcript, "r") as f:
        return f.read()


def render_jinja_template(production_time, word_count):
    """Render the Jinja template for an episode"""
    logging.info("Rendering Jinja template ...")
    episode = Episode.select().where(Episode.date == today).first()
    number = episode.number
    # number_ordinal = num2words(number, to="ordinal")
    episode_summary = create_episode_summary(get_content(), str(number))
    articles = Article.select().where(Article.episode == episode)
    mp3 = Mp3.select().where(Mp3.url.contains(f"{today_iso_fmt}_podcast_dist.mp3")).first()
    sources = []
    for article in articles:
        sources.append(article.source)
    lc = Locale.parse(lingo.replace("-", "_"))
    utc_dt = datetime.now(timezone.utc) + timedelta(minutes=5)
    LSK = pytz.timezone("Africa/Lusaka")
    with open(dist_file, "w") as f:
        f.write(
            base_template.render(
                {
                    "title": today_human_readable,
                    "description": episode_summary,
                    "episode": f"{number:03}",
                    "date": utc_dt.astimezone(LSK).isoformat(),
                    "mp3_url": mp3.url,
                    "mp3_duration": format_duration(mp3.duration),
                    "mp3_size": format_filesize(mp3.filesize),
                    "enclosure_length": mp3.filesize,
                    "itunes_duration": convert_seconds_to_mmss(mp3.duration),
                    "presenter": podcast_host,
                    "locale_id": lingo,
                    "locale_name": lc.display_name,
                    "production_time": format_duration(production_time),
                    "word_count": f"{word_count:,}",
                    "speaking_rate": words_per_minute(mp3.duration, word_count),
                    "num_articles": len(articles),
                    "num_sources": len(set(sources)),
                    "articles": [
                        {"source": article.source, "url": article.url, "title": f'"{article.title}"'}
                        for article in articles
                    ],
                }
            ),
        )
