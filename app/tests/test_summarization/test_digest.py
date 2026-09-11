import unittest
from datetime import date
from unittest.mock import MagicMock, patch

import dspy
from dspy.utils.dummies import DummyLM

from app.core.summarization.digest import (
    EVAL_ARTICLES_PATH,
    DigestGenerator,
    build_continuity_eval_set,
    build_eval_set,
    build_related_context,
    digest_compliance_score,
    format_elapsed,
    format_related_context,
    gather_related_context,
    generate_digest,
    has_canonical_sections,
    has_category_grouped_other_stories,
    has_html,
    has_intro_paragraph,
    has_markdown_links,
    has_numbered_main_stories,
    has_title_heading,
    has_why_this_matters_label,
    load_continuity_eval_cases,
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

    def test_generate_digest_passes_related_context_to_the_model(self):
        articles = [{"source": "ZNBC", "url": "http://znbc.co.zm/news/1", "title": "Title 1", "content": "Content 1"}]
        dummy_lm = DummyLM([{"digest": "generated"}])

        with dspy.context(lm=dummy_lm):
            generate_digest(articles, related_context="12 days ago: Old story\n  Old content")

        prompt = dummy_lm.history[-1]["messages"][-1]["content"]
        self.assertIn("12 days ago: Old story", prompt)

    def test_digest_generator_forward_passes_related_context_through(self):
        dummy_lm = DummyLM([{"digest": "generated"}])

        with dspy.context(lm=dummy_lm):
            DigestGenerator()(articles="1. Title (source: X)\nContent", related_context="6 months ago: Old story")

        prompt = dummy_lm.history[-1]["messages"][-1]["content"]
        self.assertIn("6 months ago: Old story", prompt)


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

    def test_has_numbered_main_stories_true_for_compliant_digest(self):
        self.assertTrue(has_numbered_main_stories(COMPLIANT_DIGEST))

    def test_has_numbered_main_stories_false_when_unnumbered(self):
        text = COMPLIANT_DIGEST.replace("1. Title 1", "**Title 1**")
        self.assertFalse(has_numbered_main_stories(text))

    def test_has_category_grouped_other_stories_true_for_compliant_digest(self):
        self.assertTrue(has_category_grouped_other_stories(COMPLIANT_DIGEST))

    def test_has_category_grouped_other_stories_false_when_flat(self):
        text = COMPLIANT_DIGEST.replace("**Governance & Justice:**\n", "")
        self.assertFalse(has_category_grouped_other_stories(text))


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

        self.assertAlmostEqual(score, 6 / 8)


class TestFormatElapsed(unittest.TestCase):
    """Test cases for the human-readable elapsed-time phrasing fed to the model."""

    def setUp(self):
        self.reference = date(2026, 9, 11)

    def test_same_day_is_today(self):
        self.assertEqual(format_elapsed(self.reference, self.reference), "today")

    def test_one_day_is_yesterday(self):
        self.assertEqual(format_elapsed(date(2026, 9, 10), self.reference), "yesterday")

    def test_a_few_days_uses_days(self):
        self.assertEqual(format_elapsed(date(2026, 9, 6), self.reference), "5 days ago")

    def test_a_week_uses_singular_week(self):
        self.assertEqual(format_elapsed(date(2026, 9, 4), self.reference), "1 week ago")

    def test_multiple_weeks_uses_plural_weeks(self):
        self.assertEqual(format_elapsed(date(2026, 8, 28), self.reference), "2 weeks ago")

    def test_a_month_uses_singular_month(self):
        self.assertEqual(format_elapsed(date(2026, 8, 12), self.reference), "1 month ago")

    def test_multiple_months_uses_plural_months(self):
        self.assertEqual(format_elapsed(date(2026, 3, 11), self.reference), "6 months ago")

    def test_a_year_uses_singular_year(self):
        self.assertEqual(format_elapsed(date(2025, 9, 11), self.reference), "1 year ago")

    def test_multiple_years_uses_plural_years(self):
        self.assertEqual(format_elapsed(date(2023, 9, 11), self.reference), "3 years ago")

    def test_future_date_clamps_to_today(self):
        self.assertEqual(format_elapsed(date(2026, 9, 12), self.reference), "today")


class TestFormatRelatedContext(unittest.TestCase):
    """Test cases for formatting `find_related_articles` matches into signature input."""

    def setUp(self):
        self.reference = date(2026, 9, 11)

    def test_empty_matches_returns_empty_string(self):
        self.assertEqual(format_related_context([], self.reference), "")

    def test_single_match_includes_elapsed_time_and_title(self):
        matches = [{"title": "Old Story", "content": "Some content.", "date": date(2026, 8, 30)}]

        result = format_related_context(matches, self.reference)

        self.assertIn("1 week ago", result)
        self.assertIn("Old Story", result)
        self.assertIn("Some content.", result)

    def test_multiple_matches_are_all_included(self):
        matches = [
            {"title": "Recent Story", "content": "Recent content.", "date": date(2026, 9, 9)},
            {"title": "Old Story", "content": "Old content.", "date": date(2026, 3, 11)},
        ]

        result = format_related_context(matches, self.reference)

        self.assertIn("Recent Story", result)
        self.assertIn("Old Story", result)
        self.assertIn("6 months ago", result)

    def test_long_content_is_truncated(self):
        matches = [{"title": "Old Story", "content": "x" * 600, "date": date(2026, 8, 30)}]

        result = format_related_context(matches, self.reference)

        self.assertIn("…", result)
        self.assertNotIn("x" * 600, result)


class TestBuildRelatedContext(unittest.TestCase):
    """Test cases for combining multiple articles' related matches into one input block."""

    def setUp(self):
        self.reference = date(2026, 9, 11)

    def test_no_articles_returns_empty_string(self):
        self.assertEqual(build_related_context([], self.reference), "")

    def test_article_with_no_matches_is_excluded(self):
        articles_with_matches = [({"title": "Title 1"}, [])]

        self.assertEqual(build_related_context(articles_with_matches, self.reference), "")

    def test_same_day_matches_are_dropped(self):
        """A same-day match is another article from today's own batch, not real continuity."""
        articles_with_matches = [
            ({"title": "Title 1"}, [{"title": "Sibling Story", "content": "C", "date": self.reference}])
        ]

        self.assertEqual(build_related_context(articles_with_matches, self.reference), "")

    def test_past_match_is_included_and_labelled_by_article(self):
        articles_with_matches = [
            ({"title": "Title 1"}, [{"title": "Old Story", "content": "Old content", "date": date(2026, 8, 1)}])
        ]

        result = build_related_context(articles_with_matches, self.reference)

        self.assertIn('Regarding "Title 1"', result)
        self.assertIn("Old Story", result)
        self.assertIn("1 month ago", result)

    def test_mixes_past_and_same_day_matches_for_one_article(self):
        articles_with_matches = [
            (
                {"title": "Title 1"},
                [
                    {"title": "Sibling Story", "content": "C", "date": self.reference},
                    {"title": "Old Story", "content": "Old content", "date": date(2026, 8, 1)},
                ],
            )
        ]

        result = build_related_context(articles_with_matches, self.reference)

        self.assertIn("Old Story", result)
        self.assertNotIn("Sibling Story", result)

    def test_only_articles_with_qualifying_matches_are_included(self):
        articles_with_matches = [
            ({"title": "Title 1"}, [{"title": "Old Story", "content": "Old content", "date": date(2026, 8, 1)}]),
            ({"title": "Title 2"}, []),
        ]

        result = build_related_context(articles_with_matches, self.reference)

        self.assertIn("Title 1", result)
        self.assertNotIn("Title 2", result)


class TestGatherRelatedContext(unittest.TestCase):
    """Test cases for looking up and formatting related context for a batch of articles."""

    def setUp(self):
        self.reference = date(2026, 9, 11)

    @patch("app.core.summarization.digest.find_related_articles")
    def test_looks_up_and_formats_matches_for_a_saved_article(self, mock_find_related):
        news = [{"url": "https://example.com/1", "title": "Title 1"}]
        saved_article = MagicMock()
        mock_find_related.return_value = [{"title": "Old Story", "content": "Old content", "date": date(2026, 8, 1)}]

        result = gather_related_context(news, {"https://example.com/1": saved_article}, self.reference)

        mock_find_related.assert_called_once_with(saved_article)
        self.assertIn('Regarding "Title 1"', result)
        self.assertIn("Old Story", result)

    @patch("app.core.summarization.digest.find_related_articles")
    def test_skips_articles_missing_from_saved_articles(self, mock_find_related):
        news = [{"url": "https://example.com/1", "title": "Title 1"}]

        result = gather_related_context(news, {}, self.reference)

        mock_find_related.assert_not_called()
        self.assertEqual(result, "")

    @patch("app.core.summarization.digest.find_related_articles")
    def test_no_news_returns_empty_string(self, mock_find_related):
        result = gather_related_context([], {}, self.reference)

        mock_find_related.assert_not_called()
        self.assertEqual(result, "")


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


class TestContinuityEvalSet(unittest.TestCase):
    """Test cases for the synthetic story-continuity eval fixtures (STORY_CONTINUITY_PLAN.md Phase 4)."""

    def setUp(self):
        self.reference = date(2026, 9, 11)

    def test_load_continuity_eval_cases_returns_both_scenarios(self):
        cases = load_continuity_eval_cases()

        self.assertEqual({case["case"] for case in cases}, {"recent_follow_up", "old_recurring_match"})

    def test_rejects_a_match_referencing_an_unknown_article_title(self):
        cases = [
            {
                "case": "broken",
                "articles": [{"source": "S", "url": "u", "title": "Real Title", "content": "C"}],
                "matches": [{"article_title": "Typo'd Title", "title": "Old", "content": "C", "days_ago": 10}],
            }
        ]

        with self.assertRaises(AssertionError):
            build_continuity_eval_set(cases, self.reference)

    def test_build_continuity_eval_set_returns_one_example_per_case(self):
        cases = load_continuity_eval_cases()

        examples = build_continuity_eval_set(cases, self.reference)

        self.assertEqual(len(examples), len(cases))

    def test_examples_mark_both_fields_as_inputs(self):
        cases = load_continuity_eval_cases()

        examples = build_continuity_eval_set(cases, self.reference)

        for example in examples:
            self.assertEqual(set(example.inputs().keys()), {"articles", "related_context"})

    def test_recent_follow_up_case_frames_as_a_short_gap(self):
        cases = load_continuity_eval_cases()

        [example] = [
            build_continuity_eval_set([case], self.reference)[0] for case in cases if case["case"] == "recent_follow_up"
        ]

        self.assertIn(
            'Regarding "Government to Review Fuel Subsidy Formula After Public Outcry"', example.related_context
        )
        self.assertIn("Fuel Pump Prices Rise for Third Time This Year", example.related_context)
        self.assertIn("6 days ago", example.related_context)
        # The unrelated filler article in this case must not pick up a continuity claim
        self.assertNotIn("Chipolopolo Under-20 Squad", example.related_context)

    def test_old_recurring_match_case_frames_as_a_long_gap(self):
        cases = load_continuity_eval_cases()

        [example] = [
            build_continuity_eval_set([case], self.reference)[0]
            for case in cases
            if case["case"] == "old_recurring_match"
        ]

        self.assertIn(
            'Regarding "ZESCO Unveils New Load-Shedding Schedule as Kariba Water Levels Drop"', example.related_context
        )
        self.assertIn("ZESCO Implements Load-Shedding Amid Generation Deficit", example.related_context)
        self.assertIn("7 months ago", example.related_context)
        # The unrelated filler article in this case must not pick up a continuity claim
        self.assertNotIn("Traders Count Losses", example.related_context)


if __name__ == "__main__":
    unittest.main()
