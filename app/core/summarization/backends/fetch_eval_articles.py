"""Fetch real articles and save them as the local DSPy eval fixture.

Not committed to git (real news, goes stale, gets rescraped). Run with
`invoke fetch-eval-articles` whenever you need fresh eval data.
"""

import json

from app.core.news.fetch import get_latest_news
from app.core.summarization.backends.dspy_backend import EVAL_ARTICLES_PATH


def main() -> None:
    articles = get_latest_news()
    EVAL_ARTICLES_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVAL_ARTICLES_PATH.write_text(json.dumps(articles, indent=2, ensure_ascii=False))
    print(f"saved {len(articles)} articles to {EVAL_ARTICLES_PATH}")


if __name__ == "__main__":
    main()
