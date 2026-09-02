"""Run BootstrapFewShot against eleventify.py's digest description signature.

Dev-only: hits the real Together model, costs real API calls. Run with
`invoke optimize-eleventify`. Saves the compiled program (gitignored, same
policy as the eval fixtures: real generated content, not committed).
"""

import dspy
from dspy.teleprompt import BootstrapFewShot

from app.core.summarization.eleventify import (
    DESCRIPTION_COMPILED_PROGRAM_PATH,
    DIGEST_DESCRIPTION_COMPLIANCE_RULES,
    DigestDescriptionGenerator,
    build_digest_description_eval_set,
    digest_description_compliance_score,
    load_eval_digests,
)
from app.core.utilities import TOGETHER_API_KEY


def evaluate(module: dspy.Module, eval_set: list[dspy.Example]) -> tuple[float, dict[str, int]]:
    """Score a module's generations against the eval set, rule by rule."""
    texts = [module(digest=example.digest).description for example in eval_set]
    scores = [digest_description_compliance_score(None, dspy.Prediction(description=text)) for text in texts]
    passes = {rule: sum(check(text) for text in texts) for rule, check in DIGEST_DESCRIPTION_COMPLIANCE_RULES.items()}
    return sum(scores) / len(scores), passes


def main() -> None:
    lm = dspy.LM("together_ai/Qwen/Qwen3.5-9B", api_key=TOGETHER_API_KEY, max_tokens=300, reasoning={"enabled": False})
    dspy.configure(lm=lm)

    eval_set = build_digest_description_eval_set(load_eval_digests())
    print(f"eval set: {len(eval_set)} examples")

    baseline = DigestDescriptionGenerator()
    baseline_score, baseline_passes = evaluate(baseline, eval_set)
    print(f"baseline compliance: {baseline_score:.2f}")
    for rule, count in baseline_passes.items():
        print(f"  {rule}: {count}/{len(eval_set)} passed")

    optimizer = BootstrapFewShot(
        metric=digest_description_compliance_score,
        metric_threshold=1.0,
        max_bootstrapped_demos=2,
        max_labeled_demos=2,
    )
    optimized = optimizer.compile(DigestDescriptionGenerator(), trainset=eval_set)
    optimized_score, optimized_passes = evaluate(optimized, eval_set)
    print(f"optimized compliance: {optimized_score:.2f}")
    for rule, count in optimized_passes.items():
        print(f"  {rule}: {count}/{len(eval_set)} passed")

    DESCRIPTION_COMPILED_PROGRAM_PATH.parent.mkdir(parents=True, exist_ok=True)
    optimized.save(str(DESCRIPTION_COMPILED_PROGRAM_PATH))
    print(f"saved compiled program to {DESCRIPTION_COMPILED_PROGRAM_PATH}")


if __name__ == "__main__":
    main()
