from peewee import AutoField, BooleanField, CharField, DateField, ForeignKeyField, IntegerField, Model, TextField

from app.core.db.config import database
from app.core.utilities import today


class BaseModel(Model):
    class Meta:
        database = database


class Mp3(BaseModel):
    """An MP3 file for a podcast episode"""

    url = CharField(max_length=2047)
    filesize = IntegerField()
    duration = IntegerField()

    class Meta:
        table_name = "mp3"

    def __str__(self):
        return self.url


class Episode(BaseModel):
    """A podcast episode"""

    number = AutoField()
    live = BooleanField(default=False)
    date = DateField(default=today)
    title = CharField(max_length=255)
    description = CharField(max_length=255)
    presenter = CharField(max_length=255)
    # https://babel.pocoo.org/en/latest/locale.html
    locale = CharField(default="en_ZA")
    mp3 = ForeignKeyField(column_name="mp3_id", field="id", model=Mp3, unique=True, backref="episode")
    time_to_produce = IntegerField()
    word_count = IntegerField()

    class Meta:
        table_name = "episode"

    def __str__(self):
        return f"Episode {self.number:03} ({self.date.isoformat()})"


class Article(BaseModel):
    """An article fetched from an online source"""

    # core fields based on fetched data
    source = CharField(max_length=255)
    url = CharField(max_length=2047)
    title = CharField(max_length=511)
    content = TextField()
    category = CharField(max_length=255, null=True)

    # additional fields
    date = DateField(default=today)
    summary = TextField(null=True)
    episode = ForeignKeyField(column_name="episode_id", field="number", model=Episode, null=True, backref="articles")

    class Meta:
        table_name = "article"

    def __str__(self):
        return self.title
