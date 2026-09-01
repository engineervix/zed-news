import unittest

import dspy
from dspy.utils.dummies import DummyLM

from app.core.summarization.backends.dspy_eleventify_backend import (
    DIGEST_DESCRIPTION_COMPLIANCE_RULES,
    build_digest_description_eval_set,
    digest_description_compliance_score,
    generate_digest_description,
    has_brief_length,
    has_code_fence,
    has_newline,
    has_unwanted_preamble,
)

COMPLIANT_DESCRIPTION = "Zambia's football team beat Malawi 2-1, and fuel prices held steady for a third month."


class TestDigestDescriptionGenerator(unittest.TestCase):
    def test_generate_digest_description_returns_predicted_text(self):
        with dspy.context(lm=DummyLM([{"description": "A brief look at today's top Zambian stories."}])):
            description = generate_digest_description(digest="1. Title 1 (source: ZNBC)\nContent 1")

        self.assertEqual(description, "A brief look at today's top Zambian stories.")


class TestDigestDescriptionComplianceRules(unittest.TestCase):
    def test_has_brief_length_true_for_two_sentences(self):
        self.assertTrue(has_brief_length(COMPLIANT_DESCRIPTION))

    def test_has_brief_length_false_for_empty(self):
        self.assertFalse(has_brief_length(""))

    def test_has_brief_length_false_for_too_many_sentences(self):
        text = "One. Two. Three. Four."
        self.assertFalse(has_brief_length(text))

    def test_has_unwanted_preamble_true_when_present(self):
        self.assertTrue(has_unwanted_preamble("Here's a brief description of today's digest."))

    def test_has_unwanted_preamble_false_when_absent(self):
        self.assertFalse(has_unwanted_preamble(COMPLIANT_DESCRIPTION))

    def test_has_code_fence_true_when_present(self):
        self.assertTrue(has_code_fence("```\nA description.\n```"))

    def test_has_code_fence_false_when_absent(self):
        self.assertFalse(has_code_fence(COMPLIANT_DESCRIPTION))

    def test_has_newline_true_when_multiline(self):
        self.assertTrue(has_newline("First line.\nSecond line."))

    def test_has_newline_false_when_single_line(self):
        self.assertFalse(has_newline(COMPLIANT_DESCRIPTION))


class TestDigestDescriptionComplianceScore(unittest.TestCase):
    def test_full_score_for_compliant_description(self):
        pred = dspy.Prediction(description=COMPLIANT_DESCRIPTION)

        score = digest_description_compliance_score(None, pred)

        self.assertEqual(score, 1.0)

    def test_reduced_score_for_violations(self):
        pred = dspy.Prediction(description="Here's the description:\n```\nOne. Two. Three.\n```")

        score = digest_description_compliance_score(None, pred)

        self.assertEqual(score, 0.0)


class TestBuildDigestDescriptionEvalSet(unittest.TestCase):
    def test_build_eval_set_has_digest_input(self):
        digests = [f"Digest number {i}" for i in range(5)]

        examples = build_digest_description_eval_set(digests)

        self.assertEqual(len(examples), 5)
        self.assertEqual(list(examples[0].inputs().keys()), ["digest"])
        self.assertEqual(examples[0].digest, "Digest number 0")


class TestComplianceRuleDict(unittest.TestCase):
    def test_all_rules_pass_for_compliant_description(self):
        for name, check in DIGEST_DESCRIPTION_COMPLIANCE_RULES.items():
            with self.subTest(rule=name):
                self.assertTrue(check(COMPLIANT_DESCRIPTION))


if __name__ == "__main__":
    unittest.main()
