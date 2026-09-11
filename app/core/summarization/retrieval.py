from datetime import date

from app.core.db.models import Article


def find_related_articles(
    article: Article,
    top_k: int = 3,
    max_distance: float | None = None,
    reference_date: date | None = None,
) -> list[dict]:
    """Find the most similar past articles to `article` by embedding cosine distance.

    No lookback cutoff - an old but genuinely similar match (a recurring topic) is
    useful continuity context, not noise. `max_distance` is unset by default: a real
    distance cutoff needs tuning against eval results, not a guessed number.

    `reference_date`, when given, excludes articles dated on or after it (e.g. today's
    own batch) before `top_k` is applied - if today's own near-duplicate coverage fills
    every slot, a real older match never gets fetched at all.
    """
    if article.embedding is None:
        return []

    distance = Article.embedding.cosine_distance(article.embedding)
    query = (
        Article.select(Article, distance.alias("distance"))
        .where(Article.embedding.is_null(False), Article.id != article.id)
        .order_by(distance)
        .limit(top_k)
    )
    if max_distance is not None:
        query = query.where(distance < max_distance)
    if reference_date is not None:
        query = query.where(Article.date < reference_date)

    return [
        {
            "id": match.id,
            "title": match.title,
            "content": match.content,
            "date": match.date,
            "distance": match.distance,
        }
        for match in query
    ]
