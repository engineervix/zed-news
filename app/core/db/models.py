import re

from tortoise import fields
from tortoise.models import Model
from tortoise.validators import RegexValidator

from app.core.utilities import today


class Article(Model):
    """An article fetched from an online source"""

    # core fields based on fetched data
    source = fields.CharField(max_length=255, description="The source of the article")
    url = fields.CharField(max_length=2047, validators=[RegexValidator(r"^(http|https)://", 0)])
    title = fields.CharField(max_length=511)
    content = fields.TextField(description="The article content as fetched from the source")
    category = fields.CharField(max_length=255, required=False, null=True)

    # additional fields
    date = fields.DateField(default=today, description="The date the article was published")
    summary = fields.TextField(required=False, null=True, description="The AI generated summary of the article")
    episode = fields.ForeignKeyField("models.Episode", related_name="articles", null=True, required=False)

    class Meta:
        table_description = "Articles fetched from various sources"

    def __str__(self):
        return self.title


class MP3(Model):
    """An MP3 file for a podcast episode"""

    url = fields.CharField(max_length=2047, validators=[RegexValidator(r"^(http|https)://", 0)])
    filesize = fields.IntField(description="The size of the MP3 file in bytes")
    duration = fields.IntField(description="The duration of the MP3 file in seconds")
    episode: fields.OneToOneRelation["Episode"]

    class Meta:
        table_description = "MP3 files for podcast episodes"

    def __str__(self):
        return self.url


class Episode(Model):
    """A podcast episode"""

    number = fields.IntField(pk=True, description="Episode number")
    live = fields.BooleanField(default=False, description="Is the episode live?")
    date = fields.DateField(default=today, unique=True, description="Episode date")
    title = fields.CharField(max_length=255, description="Episode title")
    description = fields.CharField(max_length=255, description="Episode description")
    presenter = fields.CharField(max_length=255, description="Episode presenter")
    # https://babel.pocoo.org/en/latest/locale.html
    locale = fields.CharField(
        max_length=255,
        default="en_ZA",
        description="BCP 47 locale of the episode, e.g. en_GB",
        validators=[RegexValidator(r"^[a-z]{2}_[A-Z]{2}$", 0)],
    )
    mp3 = fields.OneToOneField("models.MP3", related_name="episode")
    time_to_produce = fields.IntField(description="The time it took to produce the episode in seconds")
    word_count = fields.IntField(description="The number of words in the episode")
    articles: fields.ReverseRelation["Article"]

    class Meta:
        table_description = "This table contains the podcast episodes"

    def __str__(self):
        return f"Episode {self.number:03} ({self.date.isoformat()})"
