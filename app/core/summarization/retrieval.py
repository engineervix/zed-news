from app.core.db.models import Article


def find_related_articles(article: Article, top_k: int = 3, max_distance: float | None = None) -> list[dict]:
    """Find the most similar past articles to `article` by embedding cosine distance.

    No date filter - an old but genuinely similar match (a recurring topic) is
    useful continuity context, not noise. `max_distance` is unset by default:
    a real distance cutoff needs tuning against eval results, not a guessed
    number.
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
