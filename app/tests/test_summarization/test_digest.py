import unittest

import dspy
from dspy.utils.dummies import DummyLM

from app.core.summarization.digest import (
    EVAL_ARTICLES_PATH,
    build_eval_set,
    digest_compliance_score,
    generate_digest,
    has_canonical_sections,
    has_html,
    has_intro_paragraph,
    has_markdown_links,
    has_title_heading,
    has_why_this_matters_label,
    load_eval_articles,
)

COMPLIANT_DIGEST = """Zambia saw major developments in energy and governance today.

## Main Stories
1. Title 1
   Some details.

## Other Notable Stories
**Governance & Justice:**
* A bullet point.

## Key Takeaways & Watchpoints
* A watchpoint.
"""


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


class TestComplianceRules(unittest.TestCase):
    """Test cases for the individual digest compliance rules"""

    def test_has_canonical_sections_true_for_compliant_digest(self):
        self.assertTrue(has_canonical_sections(COMPLIANT_DIGEST))

    def test_has_canonical_sections_false_when_out_of_order(self):
        swapped = (
            COMPLIANT_DIGEST.replace("## Main Stories", "## TEMP")
            .replace("## Other Notable Stories", "## Main Stories")
            .replace("## TEMP", "## Other Notable Stories")
        )
        self.assertFalse(has_canonical_sections(swapped))

    def test_has_canonical_sections_false_with_unknown_heading(self):
        text = "## Overview\nSome text\n" + COMPLIANT_DIGEST
        self.assertFalse(has_canonical_sections(text))

    def test_has_canonical_sections_false_when_missing_a_section(self):
        text = COMPLIANT_DIGEST.split("## Key Takeaways")[0]
        self.assertFalse(has_canonical_sections(text))

    def test_has_intro_paragraph_true_when_text_precedes_first_heading(self):
        self.assertTrue(has_intro_paragraph(COMPLIANT_DIGEST))

    def test_has_intro_paragraph_false_when_digest_starts_with_heading(self):
        text = "## Main Stories\n1. Title 1\n"
        self.assertFalse(has_intro_paragraph(text))

    def test_has_markdown_links_true_when_link_present(self):
        text = "See [the report](https://example.com) for details."
        self.assertTrue(has_markdown_links(text))

    def test_has_markdown_links_false_when_absent(self):
        self.assertFalse(has_markdown_links(COMPLIANT_DIGEST))

    def test_has_html_true_when_br_tag_present(self):
        self.assertTrue(has_html("Line one<br>Line two"))

    def test_has_html_false_when_absent(self):
        self.assertFalse(has_html(COMPLIANT_DIGEST))

    def test_has_why_this_matters_label_true_when_present(self):
        text = "1. Title\n   Why this matters: it affects everyone.\n"
        self.assertTrue(has_why_this_matters_label(text))

    def test_has_why_this_matters_label_false_when_absent(self):
        self.assertFalse(has_why_this_matters_label(COMPLIANT_DIGEST))

    def test_has_title_heading_true_when_single_hash_present(self):
        text = "# Zed News Digest\n" + COMPLIANT_DIGEST
        self.assertTrue(has_title_heading(text))

    def test_has_title_heading_false_when_absent(self):
        self.assertFalse(has_title_heading(COMPLIANT_DIGEST))


class TestDigestComplianceScore(unittest.TestCase):
    """Test cases for the combined compliance metric"""

    def test_full_score_for_compliant_digest(self):
        pred = dspy.Prediction(digest=COMPLIANT_DIGEST)

        score = digest_compliance_score(None, pred)

        self.assertEqual(score, 1.0)

    def test_reduced_score_for_two_violations(self):
        text = COMPLIANT_DIGEST + "\nSee [the source](https://example.com). Why this matters: a lot.\n"
        pred = dspy.Prediction(digest=text)

        score = digest_compliance_score(None, pred)

        self.assertAlmostEqual(score, 4 / 6)


class TestEvalSet(unittest.TestCase):
    """Test cases for building the DSPy optimizer eval set"""

    def setUp(self):
        self.articles = [
            {"source": "Source", "url": f"http://example.com/{i}", "title": f"Title {i}", "content": f"Content {i}"}
            for i in range(7)
        ]

    def test_build_eval_set_splits_articles_into_batches(self):
        examples = build_eval_set(self.articles, batch_size=3)

        self.assertEqual(len(examples), 3)

    def test_build_eval_set_examples_have_articles_as_input(self):
        examples = build_eval_set(self.articles, batch_size=3)

        self.assertEqual(list(examples[0].inputs().keys()), ["articles"])
        self.assertIn("Title 0", examples[0].articles)
        self.assertIn("Title 2", examples[0].articles)
        self.assertNotIn("Title 3", examples[0].articles)

    def test_build_eval_set_last_batch_has_remainder(self):
        examples = build_eval_set(self.articles, batch_size=3)

        self.assertIn("Title 6", examples[-1].articles)

    @unittest.skipUnless(EVAL_ARTICLES_PATH.exists(), "eval fixture not present locally; run the fetch script first")
    def test_load_eval_articles_returns_real_fetched_articles(self):
        articles = load_eval_articles()

        self.assertGreater(len(articles), 0)
        for article in articles:
            self.assertIn("source", article)
            self.assertIn("title", article)
            self.assertIn("content", article)


if __name__ == "__main__":
    unittest.main()
