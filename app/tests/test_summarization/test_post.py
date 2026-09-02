import unittest

import dspy
from dspy.utils.dummies import DummyLM

from app.core.summarization.post import (
    FACEBOOK_POST_COMPLIANCE_RULES,
    IMAGE_CONCEPT_COMPLIANCE_RULES,
    build_facebook_post_eval_set,
    build_image_concept_eval_set,
    facebook_post_compliance_score,
    generate_facebook_post,
    generate_image_concept,
    has_hashtags_clumped_at_end,
    has_literal_clock_time,
    has_markdown_syntax,
    has_multiple_sentences,
    has_preamble,
    has_url_at_end,
    image_concept_compliance_score,
    is_too_long,
)

COMPLIANT_POST = """Good evening, Zambia! The Chipolopolo beat Malawi 2-1 in Ndola.

Fuel prices stayed flat for a third month running, a small win for our wallets.

What do you think? Drop a comment below.

Read more: https://zednews.pages.dev/news/2026-09-01/"""


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


class TestFacebookPostComplianceRules(unittest.TestCase):
    def test_has_markdown_syntax_true_for_bold(self):
        self.assertTrue(has_markdown_syntax("This is **bold** text."))

    def test_has_markdown_syntax_true_for_bullet(self):
        self.assertTrue(has_markdown_syntax("Update:\n- First point\n- Second point"))

    def test_has_markdown_syntax_false_for_compliant_post(self):
        self.assertFalse(has_markdown_syntax(COMPLIANT_POST))

    def test_has_literal_clock_time_true_when_present(self):
        self.assertTrue(has_literal_clock_time("The event starts at 5:45PM sharp."))

    def test_has_literal_clock_time_false_when_absent(self):
        self.assertFalse(has_literal_clock_time(COMPLIANT_POST))

    def test_has_url_at_end_true_when_last_line_has_link(self):
        self.assertTrue(has_url_at_end(COMPLIANT_POST))

    def test_has_url_at_end_false_when_link_missing(self):
        self.assertFalse(has_url_at_end("A post with no link at all."))

    def test_has_hashtags_clumped_at_end_true_when_dumped(self):
        text = "Great news today.\n\n#Zambia #ZambianNews #AFCON2026"
        self.assertTrue(has_hashtags_clumped_at_end(text))

    def test_has_hashtags_clumped_at_end_false_when_woven_in(self):
        text = "Great news today for #Zambia, especially in sports.\n\nhttps://zednews.pages.dev/news/2026-09-01/"
        self.assertFalse(has_hashtags_clumped_at_end(text))

    def test_has_hashtags_clumped_at_end_false_when_absent(self):
        self.assertFalse(has_hashtags_clumped_at_end(COMPLIANT_POST))

    def test_has_hashtags_clumped_at_end_true_when_second_to_last_line(self):
        # Regression: a real generated post put the hashtag dump on its own line, with
        # the link as the actual last line - a rule checking only the last line missed it.
        text = "Great news today.\n\n#Zambia #Chipolopolo #AFCON #FuelPrices\n\nRead more: https://zednews.pages.dev/news/2026-09-02/"
        self.assertTrue(has_hashtags_clumped_at_end(text))


class TestFacebookPostComplianceScore(unittest.TestCase):
    def test_full_score_for_compliant_post(self):
        pred = dspy.Prediction(post=COMPLIANT_POST)

        score = facebook_post_compliance_score(None, pred)

        self.assertEqual(score, 1.0)

    def test_reduced_score_for_violations(self):
        text = "**Big news** at 5:45PM!\n\n#Zambia #News #Today"
        pred = dspy.Prediction(post=text)

        score = facebook_post_compliance_score(None, pred)

        self.assertEqual(score, 0.0)


class TestImageConceptComplianceRules(unittest.TestCase):
    def test_has_multiple_sentences_true_for_two_sentences(self):
        self.assertTrue(has_multiple_sentences("A scientist in a lab. A second sentence follows."))

    def test_has_multiple_sentences_false_for_one_sentence(self):
        self.assertFalse(has_multiple_sentences("A scientist examining samples in a modern lab."))

    def test_has_preamble_true_when_present(self):
        self.assertTrue(has_preamble("Here's the concept: a scientist in a lab."))

    def test_has_preamble_false_when_absent(self):
        self.assertFalse(has_preamble("A scientist examining samples in a modern lab."))

    def test_is_too_long_true_over_limit(self):
        self.assertTrue(is_too_long(" ".join(["word"] * 61)))

    def test_is_too_long_false_under_limit(self):
        self.assertFalse(is_too_long("A scientist examining samples in a modern lab."))


class TestImageConceptComplianceScore(unittest.TestCase):
    def test_full_score_for_compliant_concept(self):
        pred = dspy.Prediction(concept="A scientist examining samples in a modern lab.")

        score = image_concept_compliance_score(None, pred)

        self.assertEqual(score, 1.0)

    def test_reduced_score_for_violations(self):
        pred = dspy.Prediction(concept="Here's the concept: a scientist in a lab. And a second sentence.")

        score = image_concept_compliance_score(None, pred)

        self.assertLess(score, 1.0)


class TestBuildEvalSets(unittest.TestCase):
    def setUp(self):
        self.digests = [f"Digest number {i}" for i in range(5)]

    def test_build_facebook_post_eval_set_cycles_time_contexts(self):
        examples = build_facebook_post_eval_set(self.digests)

        self.assertEqual(len(examples), 5)
        self.assertEqual(
            [example.time_context for example in examples],
            ["morning", "afternoon", "evening", "night", "morning"],
        )
        self.assertEqual(list(examples[0].inputs().keys()), ["digest", "date", "time_context", "link"])

    def test_build_image_concept_eval_set_has_digest_input(self):
        examples = build_image_concept_eval_set(self.digests)

        self.assertEqual(len(examples), 5)
        self.assertEqual(list(examples[0].inputs().keys()), ["digest"])
        self.assertEqual(examples[0].digest, "Digest number 0")


class TestComplianceRuleDicts(unittest.TestCase):
    def test_facebook_post_compliance_rules_all_pass_for_compliant_post(self):
        for name, check in FACEBOOK_POST_COMPLIANCE_RULES.items():
            with self.subTest(rule=name):
                self.assertTrue(check(COMPLIANT_POST))

    def test_image_concept_compliance_rules_all_pass_for_compliant_concept(self):
        for name, check in IMAGE_CONCEPT_COMPLIANCE_RULES.items():
            with self.subTest(rule=name):
                self.assertTrue(check("A scientist examining samples in a modern lab."))


if __name__ == "__main__":
    unittest.main()
