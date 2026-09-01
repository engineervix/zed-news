"""Generate real digests from the eval articles fixture, save as the downstream eval fixture.

Not committed to git (real generated content, same policy as `eval_articles.json`).
Run with `invoke fetch-downstream-eval-digests`. `post.py`'s and `eleventify.py`'s
signatures all take a generated digest as input, not raw articles, so their eval
sets are built from these digests rather than from `eval_articles.json` directly.
"""

import json

import dspy

from app.core.summarization.backends.dspy_backend import EVAL_DIGESTS_PATH, build_eval_set, generate_digest_markdown, load_eval_articles
from app.core.utilities import TOGETHER_API_KEY


def main() -> None:
    """Generate one real digest per eval batch, save them as the shared downstream eval fixture."""
    dspy.configure(
        lm=dspy.LM(
            "together_ai/deepseek-ai/DeepSeek-V4-Flash-0731",
            api_key=TOGETHER_API_KEY,
            temperature=0.6,
            max_tokens=16384,
            top_p=0.95,
            reasoning={"enabled": False},
        )
    )

    eval_set = build_eval_set(load_eval_articles(), batch_size=18)
    digests = [generate_digest_markdown(example.articles) for example in eval_set]

    EVAL_DIGESTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVAL_DIGESTS_PATH.write_text(json.dumps(digests, indent=2, ensure_ascii=False))
    print(f"saved {len(digests)} digests to {EVAL_DIGESTS_PATH}")


if __name__ == "__main__":
    main()
