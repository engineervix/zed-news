import unittest

import dspy
from dspy.utils.dummies import DummyLM

from app.core.summarization.backends.dspy_eleventify_backend import generate_digest_description


class TestDigestDescriptionGenerator(unittest.TestCase):
    def test_generate_digest_description_returns_predicted_text(self):
        with dspy.context(lm=DummyLM([{"description": "A brief look at today's top Zambian stories."}])):
            description = generate_digest_description(digest="1. Title 1 (source: ZNBC)\nContent 1")

        self.assertEqual(description, "A brief look at today's top Zambian stories.")


if __name__ == "__main__":
    unittest.main()
