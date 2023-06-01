import logging

from app.core.db.models import MP3, Article, Episode
from app.core.podcast.content import get_episode_number
from app.core.utilities import lingo, podcast_host, today_human_readable, today_iso_fmt


async def add_episode_to_db(time_to_produce: int, word_count: int):
    """Create an episode entry in the database"""
    number = await get_episode_number()

    logging.info(f"Adding episode {number:03} to the database")
    mp3_file = f"{today_iso_fmt}_podcast_dist.mp3"
    mp3 = await MP3.filter(url__contains=mp3_file).first()
    data = {
        "number": number,
        # live is false at this point, because we are yet to add articles
        # date is today's date
        "title": today_human_readable,
        "description": f"Episode {number:03}",
        "presenter": podcast_host,
        "locale": lingo.replace("-", "_"),
        "mp3": mp3,
        "time_to_produce": word_count,
        "word_count": time_to_produce,
    }
    await Episode.create(**data)


async def add_articles_to_episode():
    """Add articles to an episode"""
    number = await get_episode_number()
    logging.info(f"Updating articles for episode {number:03} ...")
    episode = await Episode.filter(number=number).first()

    articles = await Article.filter(date=episode.date).all()
    for article in articles:
        await article.update(episode=episode)

    await episode.update(live=True)
