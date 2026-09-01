import unittest

import dspy
from dspy.utils.dummies import DummyLM

from app.core.summarization.backends.dspy_backend import generate_digest


class TestDSPyDigestBackend(unittest.TestCase):
    """Test cases for the DSPy-based digest generation backend"""

    def test_generate_digest_with_no_articles_returns_none(self):
        result = generate_digest([])

        self.assertIsNone(result)

    def test_generate_digest_returns_structured_digest(self):
        articles = [
            {
                "source": "ZNBC",
                "url": "http://znbc.co.zm/news/1",
                "title": "Title 1",
                "content": "Content 1",
                "category": "National",
            }
        ]
        generated_markdown = "## Main Stories\n1. Title 1\n   Some details."
        dummy_lm = DummyLM([{"digest": generated_markdown}])

        with dspy.context(lm=dummy_lm):
            result = generate_digest(articles)

        self.assertEqual(result.content, generated_markdown)
        self.assertEqual(result.total_articles, 1)
        self.assertEqual(result.sources, ["ZNBC"])


if __name__ == "__main__":
    unittest.main()
