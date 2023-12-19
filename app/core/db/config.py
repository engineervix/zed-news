from peewee import PostgresqlDatabase

from app.core.utilities import DATABASE_HOST, DATABASE_NAME, DATABASE_PASSWORD, DATABASE_USER

database = PostgresqlDatabase(
    DATABASE_NAME,
    **{"host": DATABASE_HOST, "user": DATABASE_USER, "password": DATABASE_PASSWORD},
)


def initialize_database():
    from app.core.db.models import Article, Episode, Mp3

    database.connect()
    database.create_tables([Mp3, Episode, Article], safe=True)


def close_database():
    if not database.is_closed():
        database.close()
