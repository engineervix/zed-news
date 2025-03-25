import logging

from app.core.db.models import Article, Episode, Mp3
from app.core.podcast.content import get_episode_number
from app.core.utilities import lingo, podcast_host, today_human_readable, today_iso_fmt


def add_episode_to_db(time_to_produce: int, word_count: int):
    """Create an episode entry in the database"""
    number = get_episode_number()

    logging.info(f"Adding episode {number:03} to the database")
    mp3_file = f"{today_iso_fmt}_podcast_dist.mp3"
    mp3 = Mp3.select().where(Mp3.url.contains(mp3_file)).first()
    data = {
        "number": number,
        # live is false at this point, because we are yet to add articles
        # date is today's date
        "title": today_human_readable,
        "description": f"Episode {number:03}",
        "presenter": podcast_host,
        "locale": lingo.replace("-", "_"),
        "mp3": mp3,
        "time_to_produce": time_to_produce,
        "word_count": word_count,
    }
    Episode.create(**data)


def add_articles_to_episode():
    """Add articles to an episode"""
    number = get_episode_number()
    logging.info(f"Updating articles for episode {number:03} ...")
    episode = Episode.select().where(Episode.number == number).first()

    articles = Article.select().where(Article.date == episode.date)
    for article in articles:
        Article.update(episode=episode).where(Article.id == article.id).execute()

    Episode.update(live=True).where(Episode.number == episode.number).execute()
