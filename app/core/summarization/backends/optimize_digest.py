"""Run BootstrapFewShot against the eval set and compare to the unoptimized module.

Dev-only: hits the real Together model, costs real API calls. Run with
`invoke optimize-digest`. Saves the compiled program (gitignored, same
policy as the eval fixture: real generated content, not committed).
"""

import dspy
from dspy.teleprompt import BootstrapFewShot

from app.core.summarization.backends.dspy_backend import (
    COMPILED_PROGRAM_PATH,
    COMPLIANCE_RULES,
    DigestGenerator,
    build_eval_set,
    digest_compliance_score,
    load_eval_articles,
)
from app.core.utilities import DATA_DIR, TOGETHER_API_KEY


def evaluate(module: dspy.Module, eval_set: list[dspy.Example]) -> tuple[float, dict[str, int]]:
    """Score a module's generations against the eval set, rule by rule.

    Args:
        module: A digest-generating DSPy module, called with each example's `articles` field.
        eval_set: Examples to generate from, as built by `build_eval_set`.

    Returns:
        A tuple of the average compliance score (0.0-1.0) and a dict mapping each
        `COMPLIANCE_RULES` name to how many of the generated digests passed it.
    """
    texts = [module(articles=example.articles).digest for example in eval_set]
    scores = [digest_compliance_score(None, dspy.Prediction(digest=text)) for text in texts]
    passes = {rule: sum(check(text) for text in texts) for rule, check in COMPLIANCE_RULES.items()}
    return sum(scores) / len(scores), passes


def main() -> None:
    """Score the baseline module, run BootstrapFewShot, score the result, then save it."""
    lm = dspy.LM("together_ai/deepseek-ai/DeepSeek-V4-Flash-0731", api_key=TOGETHER_API_KEY, max_tokens=4096)
    dspy.configure(lm=lm)

    eval_set = build_eval_set(load_eval_articles(), batch_size=18)
    print(f"eval set: {len(eval_set)} examples")

    baseline = DigestGenerator()
    baseline_score, baseline_passes = evaluate(baseline, eval_set)
    print(f"baseline compliance: {baseline_score:.2f}")
    for rule, count in baseline_passes.items():
        print(f"  {rule}: {count}/{len(eval_set)} passed")

    optimizer = BootstrapFewShot(
        metric=digest_compliance_score,
        metric_threshold=1.0,
        max_bootstrapped_demos=2,
        max_labeled_demos=2,
    )
    optimized = optimizer.compile(DigestGenerator(), trainset=eval_set)
    optimized_score, optimized_passes = evaluate(optimized, eval_set)
    print(f"optimized compliance: {optimized_score:.2f}")
    for rule, count in optimized_passes.items():
        print(f"  {rule}: {count}/{len(eval_set)} passed")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    optimized.save(str(COMPILED_PROGRAM_PATH))
    print(f"saved compiled program to {COMPILED_PROGRAM_PATH}")


if __name__ == "__main__":
    main()
