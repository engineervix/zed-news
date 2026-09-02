import json
import re
from collections.abc import Callable

import dspy

from app.core.summarization.backends.dspy_backend import EVAL_DIGESTS_PATH, compliance_score, load_compiled
from app.core.utilities import DATA_DIR

DESCRIPTION_COMPILED_PROGRAM_PATH = DATA_DIR / "optimized_digest_description_program.json"


class DigestDescriptionSignature(dspy.Signature):
    """Write a very brief description of a daily Zambian news digest.

    Capture the main themes and most significant stories of the day. Focus on what
    readers will find most valuable.
    """

    digest: str = dspy.InputField(desc="The daily news digest content to describe")
    description: str = dspy.OutputField(desc="A very brief (1-2 sentence) description of the digest's main themes")


class DigestDescriptionGenerator(dspy.Module):
    """DSPy module that generates a brief description from a news digest."""

    def __init__(self) -> None:
        super().__init__()
        self.generate = dspy.Predict(DigestDescriptionSignature)

    def forward(self, digest: str) -> dspy.Prediction:
        return self.generate(digest=digest)


def load_eval_digests() -> list[str]:
    """Load the real generated digests fetched for building the downstream eval set."""
    return json.loads(EVAL_DIGESTS_PATH.read_text())


def build_digest_description_eval_set(digests: list[str]) -> list[dspy.Example]:
    """Build an eval set from real digests, one example per digest."""
    return [dspy.Example(digest=digest).with_inputs("digest") for digest in digests]


def has_brief_length(text: str, max_sentences: int = 2) -> bool:
    """Check that the description is 1-2 sentences, not empty and not a wall of text."""
    sentence_count = len(re.findall(r"[.!?]", text.strip()))
    return 0 < sentence_count <= max_sentences


def has_unwanted_preamble(text: str) -> bool:
    """Check for meta-commentary before the actual description (e.g. 'Here's the description:')."""
    first_line = text.strip().splitlines()[0].lower() if text.strip() else ""
    unwanted = ("description:", "here's", "here is", "sure")
    return first_line.startswith(unwanted)


def has_code_fence(text: str) -> bool:
    """Check for a triple-backtick code fence, which the description must not contain."""
    return "```" in text


def has_newline(text: str) -> bool:
    """Check for a newline, since the description should be a single line."""
    return "\n" in text.strip()


DIGEST_DESCRIPTION_COMPLIANCE_RULES: dict[str, Callable[[str], bool]] = {
    "brief": has_brief_length,
    "no_preamble": lambda text: not has_unwanted_preamble(text),
    "no_code_fence": lambda text: not has_code_fence(text),
    "single_line": lambda text: not has_newline(text),
}


def digest_description_compliance_score(example, pred, trace=None) -> float:
    """Score a generated digest description against the hard formatting rules, as a fraction in [0, 1]."""
    return compliance_score(DIGEST_DESCRIPTION_COMPLIANCE_RULES, pred.description)


def load_compiled_digest_description_generator() -> DigestDescriptionGenerator:
    """Load the optimizer-compiled digest description generator, if one has been synced to this machine.

    Falls back to the raw, unoptimized module when `DESCRIPTION_COMPILED_PROGRAM_PATH`
    does not exist - see `load_compiled` in `dspy_backend.py` for why.
    """
    return load_compiled(DigestDescriptionGenerator, DESCRIPTION_COMPILED_PROGRAM_PATH)


def generate_digest_description(digest: str) -> str:
    """Generate a brief digest description from a news digest using a DSPy module."""
    return load_compiled_digest_description_generator()(digest=digest).description
