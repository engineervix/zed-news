from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "mp3" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "url" VARCHAR(2047) NOT NULL,
    "filesize" INT NOT NULL,
    "duration" INT NOT NULL
);
COMMENT ON COLUMN "mp3"."filesize" IS 'The size of the MP3 file in bytes';
COMMENT ON COLUMN "mp3"."duration" IS 'The duration of the MP3 file in seconds';
COMMENT ON TABLE "mp3" IS 'MP3 files for podcast episodes';
CREATE TABLE IF NOT EXISTS "episode" (
    "number" SERIAL NOT NULL PRIMARY KEY,
    "live" BOOL NOT NULL  DEFAULT False,
    "date" DATE NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "description" VARCHAR(255) NOT NULL,
    "presenter" VARCHAR(255) NOT NULL,
    "locale" VARCHAR(255) NOT NULL  DEFAULT 'en_ZA',
    "time_to_produce" INT NOT NULL,
    "word_count" INT NOT NULL,
    "mp3_id" INT NOT NULL UNIQUE REFERENCES "mp3" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "episode"."number" IS 'Episode number';
COMMENT ON COLUMN "episode"."live" IS 'Is the episode live?';
COMMENT ON COLUMN "episode"."date" IS 'Episode date';
COMMENT ON COLUMN "episode"."title" IS 'Episode title';
COMMENT ON COLUMN "episode"."description" IS 'Episode description';
COMMENT ON COLUMN "episode"."presenter" IS 'Episode presenter';
COMMENT ON COLUMN "episode"."locale" IS 'BCP 47 locale of the episode, e.g. en_GB';
COMMENT ON COLUMN "episode"."time_to_produce" IS 'The time it took to produce the episode in seconds';
COMMENT ON COLUMN "episode"."word_count" IS 'The number of words in the episode';
COMMENT ON TABLE "episode" IS 'This table contains the podcast episodes';
CREATE TABLE IF NOT EXISTS "article" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "source" VARCHAR(255) NOT NULL,
    "url" VARCHAR(2047) NOT NULL,
    "title" VARCHAR(511) NOT NULL,
    "content" TEXT NOT NULL,
    "category" VARCHAR(255),
    "date" DATE NOT NULL,
    "summary" TEXT,
    "episode_id" INT REFERENCES "episode" ("number") ON DELETE CASCADE
);
COMMENT ON COLUMN "article"."source" IS 'The source of the article';
COMMENT ON COLUMN "article"."content" IS 'The article content as fetched from the source';
COMMENT ON COLUMN "article"."date" IS 'The date the article was published';
COMMENT ON COLUMN "article"."summary" IS 'The AI generated summary of the article';
COMMENT ON TABLE "article" IS 'Articles fetched from various sources';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
