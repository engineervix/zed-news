"""One-off schema migration: add `article.embedding` + its HNSW index.

Run once per database (local now, then again against Neon at deploy time)
via `invoke add-embedding-column`.
`tasks.py`'s `migrate`/`upgrade` tasks shell out to `aerich` (a Tortoise ORM
tool that isn't even a dependency here - this project uses peewee) and don't
work, so this is a real one-off script instead.

Uses `playhouse.migrate` for the column add, but raw SQL for the extension
and index: peewee's `SchemaMigrator.add_index` builds plain column
references and can't express pgvector's operator-class syntax
(`vector_cosine_ops`), and `Model.add_index` only registers metadata for a
future `create_table()` - neither actually runs DDL against a table that
already exists.
"""

from playhouse.migrate import PostgresqlMigrator, migrate

from app.core.db.config import database
from app.core.db.models import Article


def column_exists(table: str, column: str) -> bool:
    cursor = database.execute_sql(
        "SELECT 1 FROM information_schema.columns WHERE table_name = %s AND column_name = %s",
        (table, column),
    )
    return cursor.fetchone() is not None


def main() -> None:
    database.connect(reuse_if_open=True)

    database.execute_sql("CREATE EXTENSION IF NOT EXISTS vector")
    print("vector extension: ok")

    if column_exists("article", "embedding"):
        print("embedding column: already exists, skipping")
    else:
        migrator = PostgresqlMigrator(database)
        migrate(migrator.add_column("article", "embedding", Article.embedding))
        print("embedding column: added")

    # HNSW needs no training step, so this is safe even before the backfill runs.
    database.execute_sql(
        "CREATE INDEX IF NOT EXISTS article_embedding_hnsw_idx ON article USING hnsw (embedding vector_cosine_ops)"
    )
    print("hnsw index: ok")

    database.close()


if __name__ == "__main__":
    main()
