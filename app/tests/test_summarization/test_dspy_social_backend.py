import unittest

import dspy
from dspy.utils.dummies import DummyLM

from app.core.summarization.backends.dspy_social_backend import generate_facebook_post, generate_image_concept


class TestFacebookPostGenerator(unittest.TestCase):
    def test_generate_facebook_post_returns_predicted_text(self):
        with dspy.context(lm=DummyLM([{"post": "Good morning Zambia! Here's today's news. #Zambia"}])):
            post_text = generate_facebook_post(
                digest="1. Title 1 (source: ZNBC)\nContent 1",
                date="Monday, 1 September 2026",
                time_context="morning",
                link="https://zednews.pages.dev/news/2026-09-01/",
            )

        self.assertEqual(post_text, "Good morning Zambia! Here's today's news. #Zambia")


class TestImageConceptGenerator(unittest.TestCase):
    def test_generate_image_concept_returns_predicted_text(self):
        with dspy.context(lm=DummyLM([{"concept": "A scientist examining samples in a modern lab."}])):
            concept = generate_image_concept(digest="1. Title 1 (source: ZNBC)\nContent 1")

        self.assertEqual(concept, "A scientist examining samples in a modern lab.")


if __name__ == "__main__":
    unittest.main()
