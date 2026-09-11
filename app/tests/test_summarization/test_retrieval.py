import unittest
from datetime import timedelta

from app.core.db.config import close_database, initialize_database
from app.core.db.models import Article
from app.core.summarization.retrieval import find_related_articles


class TestFindRelatedArticles(unittest.TestCase):
    """Integration test against the real local Postgres container - pgvector's
    cosine-distance operator is Postgres-only, the SQLite in-memory pattern
    used elsewhere in this repo's tests can't run it.
    """

    @classmethod
    def setUpClass(cls):
        initialize_database()

    @classmethod
    def tearDownClass(cls):
        close_database()

    def setUp(self):
        # Real 1024-dim vectors, not random - direction is what cosine distance
        # measures, so these are built to have an unambiguous, hand-verifiable
        # ordering: "near" points almost the same way as "query", "far" points
        # a fully orthogonal way (cosine distance exactly 1.0 from "query").
        query_vec = [0.0] * 1024
        query_vec[0] = 1.0

        near_vec = [0.0] * 1024
        near_vec[0] = 0.99
        near_vec[1] = 0.14

        far_vec = [0.0] * 1024
        far_vec[1] = 1.0

        self.query_article = Article.create(
            source="test",
            url="https://test.example/query",
            title="Query article",
            content="query content",
            embedding=query_vec,
        )
        self.near_article = Article.create(
            source="test",
            url="https://test.example/near",
            title="Near article",
            content="near content",
            embedding=near_vec,
        )
        self.far_article = Article.create(
            source="test",
            url="https://test.example/far",
            title="Far article",
            content="far content",
            embedding=far_vec,
        )
        self.no_embedding_article = Article.create(
            source="test",
            url="https://test.example/none",
            title="No embedding article",
            content="no embedding content",
            embedding=None,
        )
        self.article_ids = [
            self.query_article.id,
            self.near_article.id,
            self.far_article.id,
            self.no_embedding_article.id,
        ]

    def tearDown(self):
        Article.delete().where(Article.id.in_(self.article_ids)).execute()

    def test_nearest_match_is_the_article_closest_in_embedding_space(self):
        # near_vec's cosine similarity to query_vec (~0.99) is high enough that
        # no real article in this dev DB's 13k+ backfilled rows (dense, spread
        # across all 1024 dims) can plausibly beat it - safe against real data.
        results = find_related_articles(self.query_article, top_k=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.near_article.id)
        self.assertEqual(results[0]["title"], "Near article")

    def test_relative_ordering_holds_against_the_full_real_corpus(self):
        # Don't assert far_article's exact rank among 13k+ real rows (some real
        # article could plausibly score between near and far) - only that
        # near ranks strictly ahead of far, which distance construction guarantees
        # regardless of what real noise sits between them.
        total_articles = Article.select().count()
        results = find_related_articles(self.query_article, top_k=total_articles)

        result_ids = [r["id"] for r in results]
        self.assertLess(result_ids.index(self.near_article.id), result_ids.index(self.far_article.id))

    def test_excludes_the_queried_article_itself(self):
        results = find_related_articles(self.query_article, top_k=5)
        self.assertNotIn(self.query_article.id, [r["id"] for r in results])

    def test_excludes_articles_without_an_embedding(self):
        results = find_related_articles(self.query_article, top_k=Article.select().count())
        self.assertNotIn(self.no_embedding_article.id, [r["id"] for r in results])

    def test_each_match_carries_its_real_date_and_content(self):
        # Phase 4 needs the real date/content to frame continuity correctly,
        # not just a bare distance score.
        results = find_related_articles(self.query_article, top_k=1)

        self.assertEqual(results[0]["date"], self.near_article.date)
        self.assertEqual(results[0]["content"], "near content")

    def test_max_distance_excludes_matches_beyond_the_threshold(self):
        # near_vec's cosine distance to query_vec is ~0.01, far_vec's is exactly
        # 1.0 (orthogonal) - 0.5 sits strictly between them, so this threshold
        # keeps near_article and excludes far_article specifically.
        results = find_related_articles(self.query_article, top_k=10, max_distance=0.5)

        result_ids = [r["id"] for r in results]
        self.assertIn(self.near_article.id, result_ids)
        self.assertNotIn(self.far_article.id, result_ids)

    def test_returns_empty_list_when_the_query_article_has_no_embedding(self):
        results = find_related_articles(self.no_embedding_article, top_k=3)
        self.assertEqual(results, [])

    def test_reference_date_excludes_same_day_matches_before_top_k_is_applied(self):
        # today_duplicate is nearer to query_vec than older_match, so with no date
        # filter it alone would fill a top_k=1 budget - the bug this guards against:
        # filtering same-day matches out *after* limit() would still drop
        # older_match here, since today_duplicate already took the only slot.
        reference_date = self.query_article.date

        today_duplicate_vec = [0.0] * 1024
        today_duplicate_vec[0] = 0.999
        today_duplicate = Article.create(
            source="test",
            url="https://test.example/today-duplicate",
            title="Today duplicate",
            content="today duplicate content",
            embedding=today_duplicate_vec,
            date=reference_date,
        )
        self.article_ids.append(today_duplicate.id)

        older_match_vec = [0.0] * 1024
        older_match_vec[0] = 0.99
        older_match_vec[1] = 0.14
        older_match = Article.create(
            source="test",
            url="https://test.example/older-match",
            title="Older match",
            content="older match content",
            embedding=older_match_vec,
            date=reference_date - timedelta(days=30),
        )
        self.article_ids.append(older_match.id)

        results = find_related_articles(self.query_article, top_k=1, reference_date=reference_date)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], older_match.id)


if __name__ == "__main__":
    unittest.main()
