import logging

from babel import Locale
from jinja2 import Environment, PackageLoader, select_autoescape
from num2words import num2words

from app.core.db.models import MP3, Article, Episode
from app.core.utilities import (
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


async def render_jinja_template(production_time, word_count):
    """Render the Jinja template for an episode"""
    logging.info("Rendering Jinja template ...")
    episode = await Episode.filter(date=today).first()
    number = episode.number
    number_ordinal = num2words(number, to="ordinal")
    articles = await Article.filter(episode=episode).all()
    mp3 = await MP3.filter(url__contains=f"{today_iso_fmt}_podcast_dist.mp3").first()
    sources = []
    for article in articles:
        sources.append(article.source)
    lc = Locale.parse(lingo.replace("-", "_"))
    print(
        base_template.render(
            {
                "title": today_human_readable,
                "description": f"This is the {number_ordinal} episode of the podcast.",
                "episode": f"{number:03}",
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
        file=open(dist_file, "w"),
    )
