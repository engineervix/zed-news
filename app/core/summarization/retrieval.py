from datetime import date, timedelta

from app.core.db.models import Article


def find_related_articles(
    article: Article,
    top_k: int = 3,
    max_distance: float | None = None,
    reference_date: date | None = None,
    max_age_days: int | None = None,
) -> list[dict]:
    """Find the most similar past articles to `article` by embedding cosine distance.

    No lookback cutoff - an old but genuinely similar match (a recurring topic) is
    useful continuity context, not noise. `max_distance` is unset by default: a real
    distance cutoff needs tuning against eval results, not a guessed number.

    `reference_date`, when given, excludes articles dated on or after it (e.g. today's
    own batch) before `top_k` is applied - if today's own near-duplicate coverage fills
    every slot, a real older match never gets fetched at all.

    `max_age_days` additionally drops matches more than that many days before
    `reference_date`, also before `top_k` is applied. It needs `reference_date` - "within
    N days of when?" is unanswerable without it, so passing one without the other raises.
    """
    if max_age_days is not None and reference_date is None:
        raise ValueError("max_age_days requires reference_date")
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
    if max_age_days is not None:
        query = query.where(Article.date >= reference_date - timedelta(days=max_age_days))

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
