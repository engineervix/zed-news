"""One-off: embed existing articles missing `embedding`.

Dev-only, hits the real OpenRouter API - costs real API calls and, at 13k+
articles, takes a while. Run with `invoke backfill-embeddings`.
"""

import logging
import sys

from app.core.db.config import close_database, initialize_database
from app.core.db.models import Article
from app.core.summarization.embeddings import embed_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(limit: int | None = None) -> None:
    initialize_database()

    # ponytail: one embed_text() call per article (sequential). OpenRouter's
    # /v1/embeddings accepts a batch `input` array - switch to that if a
    # 13k-row backfill run is too slow in practice.
    query = Article.select().where(Article.embedding.is_null(), Article.content != "")
    if limit:
        query = query.limit(limit)
    articles = list(query)
    logger.info(f"{len(articles)} articles to embed" + (f" (limit={limit})" if limit else ""))

    failed = []
    for i, article in enumerate(articles, start=1):
        try:
            article.embedding = embed_text(article.content)
            article.save()
            logger.info(f"[{i}/{len(articles)}] embedded article {article.id}")
        except Exception:
            logger.exception(f"[{i}/{len(articles)}] failed to embed article {article.id}, continuing")
            failed.append(article.id)

    if failed:
        logger.warning(f"{len(failed)} articles failed: {failed}")

    close_database()


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
