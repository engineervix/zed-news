"""One-off: embed existing articles missing `embedding`.

Dev-only, hits the real OpenRouter API - costs real API calls and, at 13k+
articles, takes a while. Run with `invoke backfill-embeddings`.
"""

import logging
import sys

from app.core.db.config import close_database, initialize_database
from app.core.db.models import Article
from app.core.summarization.embeddings import embed_texts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BATCH_SIZE = 50


def main(limit: int | None = None) -> None:
    initialize_database()

    query = Article.select().where(Article.embedding.is_null(), Article.content != "")
    if limit:
        query = query.limit(limit)
    articles = list(query)
    logger.info(f"{len(articles)} articles to embed" + (f" (limit={limit})" if limit else ""))

    failed = []
    for start in range(0, len(articles), BATCH_SIZE):
        batch = articles[start : start + BATCH_SIZE]
        try:
            embeddings = embed_texts([a.content for a in batch])
            for article, embedding in zip(batch, embeddings, strict=True):
                article.embedding = embedding
                article.save()
            logger.info(f"[{start + len(batch)}/{len(articles)}] embedded batch of {len(batch)}")
        except Exception:
            # ponytail: whole-batch retry on failure, not per-article fallback -
            # a failed batch just leaves those rows with embedding=NULL, and
            # the script is already re-run-safe (WHERE embedding IS NULL), so
            # rerunning picks them up in a smaller batch context next time.
            logger.exception(f"batch at [{start}:{start + len(batch)}] failed, continuing")
            failed.extend(a.id for a in batch)

    if failed:
        logger.warning(f"{len(failed)} articles failed: {failed}")

    close_database()


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
