"""Build the real story-continuity eval fixture: real `find_related_articles` matches
for `eval_articles.json`, embedded via OpenRouter and queried against the live DB.

Dev-only, hits the real OpenRouter API and the real local Postgres container (13k+
backfilled articles) - costs real API calls. Run with `invoke
fetch-eval-continuity-context` after `invoke fetch-eval-articles`. Not committed to git
(real content, regenerate locally), same policy as eval_articles.json/eval_digests.json.
"""

import json
import logging
from datetime import date

from app.core.db.config import close_database, initialize_database
from app.core.db.models import Article
from app.core.summarization.digest import EVAL_CONTINUITY_CONTEXT_PATH, load_eval_articles
from app.core.summarization.embeddings import embed_texts
from app.core.summarization.retrieval import find_related_articles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BATCH_SIZE = 50


def main() -> None:
    initialize_database()

    articles = load_eval_articles()
    embeddings: list[list[float] | None] = []
    for start in range(0, len(articles), BATCH_SIZE):
        batch = articles[start : start + BATCH_SIZE]
        embeddings.extend(embed_texts([article["content"] for article in batch]))
        logger.info(f"embedded [{start + len(batch)}/{len(articles)}]")

    context: dict[str, list[dict]] = {}
    for article, embedding in zip(articles, embeddings, strict=True):
        if embedding is None:
            continue
        matches = find_related_articles(Article(embedding=embedding), top_k=3, reference_date=date.today())
        # An eval article can already sit in the live DB from a real production run that
        # scraped the same story - matching by title (retrieval doesn't expose url) drops
        # that self-match so it isn't mistaken for genuine continuity.
        matches = [match for match in matches if match["title"] != article["title"]]
        if matches:
            context[article["url"]] = [
                {"title": match["title"], "content": match["content"], "date": match["date"].isoformat()}
                for match in matches
            ]

    EVAL_CONTINUITY_CONTEXT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVAL_CONTINUITY_CONTEXT_PATH.write_text(json.dumps(context, indent=2, ensure_ascii=False))
    print(f"saved real matches for {len(context)}/{len(articles)} articles to {EVAL_CONTINUITY_CONTEXT_PATH}")

    close_database()


if __name__ == "__main__":
    main()
