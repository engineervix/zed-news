import json
import re
from collections.abc import Callable
from itertools import cycle

import dspy

from app.core.summarization.backends.dspy_backend import EVAL_DIGESTS_PATH
from app.core.utilities import DATA_DIR

FACEBOOK_POST_COMPILED_PROGRAM_PATH = DATA_DIR / "optimized_facebook_post_program.json"
IMAGE_CONCEPT_COMPILED_PROGRAM_PATH = DATA_DIR / "optimized_image_concept_program.json"
TIME_CONTEXTS = ("morning", "afternoon", "evening", "night")


class FacebookPostSignature(dspy.Signature):
    """Write an engaging Facebook post for Zed News, a patriotic Zambian news outlet,
    from the day's news digest. Your tone is passionate and engaging. Adapt your tone
    naturally to match the content - celebratory for good news, respectful for serious
    matters, informative for policy changes, and balanced for mixed content. Never
    mention specific times (like 5:45PM) in the post.

    Most readers will never click the link, so make the post completely valuable on
    its own.

    FORMATTING RULES - STRICTLY ENFORCE:
    - Use ONLY plain text with line breaks and emojis
    - NEVER use markdown syntax (**, *, _, `, #, -, etc.)
    - NEVER use bullet points (•, -, *, 1., 2., etc.)
    - NEVER use asterisks or underscores for emphasis
    - NEVER use hashtags as headers
    - NEVER put two or more hashtags together on their own line, at the end or
      anywhere else - weave at most one hashtag into the sentence of the story it
      relates to, so no line ever contains only hashtags
    - Use natural paragraph breaks and emojis for visual structure

    Craft a post that:
    - Starts with a creative, context-aware greeting suitable for the time of day
    - Presents 4-5 key stories in conversational paragraphs (NOT lists or bullet points)
    - Each story is 1-2 short sentences explaining WHAT happened and WHY it matters to
      us as Zambians
    - Uses patriotic and inclusive language (e.g. "our nation", "we", "our fellow
      citizens")
    - Uses emojis strategically (1 per story max) for visual breaks and emotion
    - Uses line breaks between stories for mobile readability
    - Includes specific numbers/facts people want to share in WhatsApp groups
    - Makes each story relatable to daily life (jobs, money, safety, family)
    - Ends with a creative, engaging call-to-action to spark conversation
    - Includes the link at the very end

    Write for mobile users scrolling fast - make it instantly valuable and shareable.
    Vary your language and avoid repetitive phrases.
    """

    digest: str = dspy.InputField(desc="Today's news digest content the post is based on")
    date: str = dspy.InputField(desc="Human-readable date the post covers")
    time_context: str = dspy.InputField(desc="Time of day: 'morning', 'afternoon', 'evening', or 'night'")
    link: str = dspy.InputField(desc="URL to include at the very end of the post")
    post: str = dspy.OutputField(desc="The Facebook post text, ready to publish")


class FacebookPostGenerator(dspy.Module):
    """DSPy module that generates Facebook post text from a news digest."""

    def __init__(self) -> None:
        super().__init__()
        self.generate = dspy.Predict(FacebookPostSignature)

    def forward(self, digest: str, date: str, time_context: str, link: str) -> dspy.Prediction:
        return self.generate(digest=digest, date=date, time_context=time_context, link=link)


class ImageConceptSignature(dspy.Signature):
    """Act as a Creative Director for Zed News, a Zambian news outlet, and describe a
    concept for a promotional image that captures the essence of today's news digest.

    The image should be symbolic, professional, and optimistic, reflecting themes of
    innovation, development, community, and national pride in Zambia. Read the digest,
    identify the most visually compelling or impactful story, and describe a single,
    clear photographic scene.

    GUIDELINES:
    - Read the entire digest to understand the key stories.
    - Select the ONE story that is most visually interesting or emotionally resonant.
    - Describe a photograph that represents this story symbolically. Do NOT be literal.
    - Depict Zambians as professionals, innovators, community members, and families.
    - The tone must be professional, hopeful, and forward-looking.
    - AVOID: clichés, poverty imagery, political figures, direct depictions of negative
      events (e.g. accidents, crime). If the news is negative, find a positive or
      neutral angle (e.g. for a cholera outbreak, show a scientist in a lab).

    Respond with ONLY the concise, one-sentence description of the photographic scene.
    Do not add any other text.
    """

    digest: str = dspy.InputField(desc="Today's news digest content to draw the image concept from")
    concept: str = dspy.OutputField(desc="A single, concise, one-sentence description of the photographic scene")


class ImageConceptGenerator(dspy.Module):
    """DSPy module that generates a promotional image concept from a news digest."""

    def __init__(self) -> None:
        super().__init__()
        self.generate = dspy.Predict(ImageConceptSignature)

    def forward(self, digest: str) -> dspy.Prediction:
        return self.generate(digest=digest)


def load_eval_digests() -> list[str]:
    """Load the real generated digests fetched for building the downstream eval sets."""
    return json.loads(EVAL_DIGESTS_PATH.read_text())


def build_facebook_post_eval_set(
    digests: list[str],
    date: str = "Tuesday, September 1st, 2026",
    link: str = "https://zednews.pages.dev/news/2026-09-01/",
) -> list[dspy.Example]:
    """Build an eval set from real digests, cycling through all four times of day."""
    time_contexts = cycle(TIME_CONTEXTS)
    return [
        dspy.Example(digest=digest, date=date, time_context=next(time_contexts), link=link).with_inputs(
            "digest", "date", "time_context", "link"
        )
        for digest in digests
    ]


def build_image_concept_eval_set(digests: list[str]) -> list[dspy.Example]:
    """Build an eval set from real digests, one example per digest."""
    return [dspy.Example(digest=digest).with_inputs("digest") for digest in digests]


def has_markdown_syntax(text: str) -> bool:
    """Check for markdown syntax (bold, code, headings, bullets, numbered lists, emphasis)."""
    return bool(re.search(r"\*\*|`|^#{1,6}\s|^[*-]\s|^\d+\.\s|_[^_\s][^_]*_", text, re.MULTILINE))


def has_literal_clock_time(text: str) -> bool:
    """Check for a literal clock time (e.g. '5:45PM'), which the post must not mention."""
    return bool(re.search(r"\b\d{1,2}:\d{2}\s*(am|pm)\b", text, re.IGNORECASE))


def has_url_at_end(text: str) -> bool:
    """Check that the last non-empty line contains a URL."""
    lines = [line for line in text.splitlines() if line.strip()]
    return bool(lines) and bool(re.search(r"https?://\S+", lines[-1]))


def has_hashtags_clumped_at_end(text: str) -> bool:
    """Check whether any line is nothing but a block of hashtags, dumped rather than woven in.

    Checks every line, not just the last one: production output often puts the link on
    its own final line, so a hashtag dump lands second-to-last, not last.
    """
    for line in text.splitlines():
        tokens = line.split()
        if not tokens:
            continue
        hashtag_tokens = [token for token in tokens if token.startswith("#")]
        if len(hashtag_tokens) >= 2 and len(hashtag_tokens) == len(tokens):
            return True
    return False


FACEBOOK_POST_COMPLIANCE_RULES: dict[str, Callable[[str], bool]] = {
    "no_markdown_syntax": lambda text: not has_markdown_syntax(text),
    "no_literal_clock_time": lambda text: not has_literal_clock_time(text),
    "url_at_end": has_url_at_end,
    "hashtags_woven_not_clumped": lambda text: not has_hashtags_clumped_at_end(text),
}


def facebook_post_compliance_score(example, pred, trace=None) -> float:
    """Score a generated Facebook post against the hard formatting rules, as a fraction in [0, 1]."""
    text = pred.post
    checks = [check(text) for check in FACEBOOK_POST_COMPLIANCE_RULES.values()]
    return sum(checks) / len(checks)


def has_multiple_sentences(text: str) -> bool:
    """Check for more than one sentence-ending punctuation mark."""
    return len(re.findall(r"[.!?]", text.strip())) > 1


def has_preamble(text: str) -> bool:
    """Check for meta-commentary before the actual concept (e.g. 'Here's the concept:')."""
    first_line = text.strip().splitlines()[0].lower() if text.strip() else ""
    unwanted = ("here's", "here is", "sure", "concept:", "scene:", "description:")
    return first_line.startswith(unwanted)


def is_too_long(text: str, max_words: int = 60) -> bool:
    """Check whether the concept exceeds a reasonable one-sentence word count."""
    return len(text.split()) > max_words


IMAGE_CONCEPT_COMPLIANCE_RULES: dict[str, Callable[[str], bool]] = {
    "single_sentence": lambda text: not has_multiple_sentences(text),
    "no_preamble": lambda text: not has_preamble(text),
    "concise": lambda text: not is_too_long(text),
}


def image_concept_compliance_score(example, pred, trace=None) -> float:
    """Score a generated image concept against the hard formatting rules, as a fraction in [0, 1]."""
    text = pred.concept
    checks = [check(text) for check in IMAGE_CONCEPT_COMPLIANCE_RULES.values()]
    return sum(checks) / len(checks)


def load_compiled_facebook_post_generator() -> FacebookPostGenerator:
    """Load the optimizer-compiled Facebook post generator, if one has been synced to this machine.

    Falls back to the raw, unoptimized module when `FACEBOOK_POST_COMPILED_PROGRAM_PATH`
    does not exist - see `load_compiled_digest_generator` in `dspy_backend.py` for why.
    """
    module = FacebookPostGenerator()
    if FACEBOOK_POST_COMPILED_PROGRAM_PATH.exists():
        module.load(str(FACEBOOK_POST_COMPILED_PROGRAM_PATH))
    return module


def load_compiled_image_concept_generator() -> ImageConceptGenerator:
    """Load the optimizer-compiled image concept generator, if one has been synced to this machine."""
    module = ImageConceptGenerator()
    if IMAGE_CONCEPT_COMPILED_PROGRAM_PATH.exists():
        module.load(str(IMAGE_CONCEPT_COMPILED_PROGRAM_PATH))
    return module


def generate_facebook_post(digest: str, date: str, time_context: str, link: str) -> str:
    """Generate Facebook post text from a news digest using a DSPy module."""
    return load_compiled_facebook_post_generator()(digest=digest, date=date, time_context=time_context, link=link).post


def generate_image_concept(digest: str) -> str:
    """Generate a promotional image concept from a news digest using a DSPy module."""
    return load_compiled_image_concept_generator()(digest=digest).concept
