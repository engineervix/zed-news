"""Run BootstrapFewShot against the eval set and compare to the unoptimized module.

Dev-only: hits the real Together model, costs real API calls. Run with
`invoke optimize-digest`. Saves the compiled program (gitignored, same
policy as the eval fixture: real generated content, not committed).
"""

from datetime import date

import dspy
from dspy.teleprompt import BootstrapFewShot

from app.core.summarization.digest import (
    COMPILED_PROGRAM_PATH,
    COMPLIANCE_RULES,
    EVAL_CONTINUITY_CONTEXT_PATH,
    DigestGenerator,
    build_continuity_eval_set,
    build_eval_set,
    build_real_continuity_eval_set,
    continuity_faithfulness_score,
    digest_compliance_score,
    exa_corroboration_score,
    load_continuity_eval_cases,
    load_eval_articles,
    load_eval_continuity_context,
)
from app.core.utilities import DATA_DIR, TOGETHER_API_KEY


def evaluate(module: dspy.Module, eval_set: list[dspy.Example]) -> tuple[float, dict[str, int], list[str]]:
    """Score a module's generations against the eval set, rule by rule.

    Args:
        module: A digest-generating DSPy module, called with each example's marked input
            fields (`articles`, plus `related_context` for the story-continuity cases).
        eval_set: Examples to generate from, as built by `build_eval_set` and
            `build_continuity_eval_set`.

    Returns:
        A tuple of the average compliance score (0.0-1.0), a dict mapping each
        `COMPLIANCE_RULES` name to how many of the generated digests passed it, and the
        raw generated texts (same order as `eval_set`) so callers can reuse them for other
        metrics instead of regenerating.
    """
    texts = [module(**example.inputs()).digest for example in eval_set]
    scores = [digest_compliance_score(None, dspy.Prediction(digest=text)) for text in texts]
    passes = {rule: sum(check(text) for text in texts) for rule, check in COMPLIANCE_RULES.items()}
    return sum(scores) / len(scores), passes, texts


def report_continuity_faithfulness(label: str, examples: list[dspy.Example], texts: list[str]) -> None:
    """Print the average `continuity_faithfulness_score` over examples that carry
    `related_context` - examples without one are skipped rather than counted as trivial
    passes, so the printed count reflects only genuine continuity claims checked.
    """
    scored = [
        continuity_faithfulness_score(example, dspy.Prediction(digest=text))
        for example, text in zip(examples, texts, strict=True)
        if getattr(example, "related_context", "")
    ]
    if not scored:
        return
    print(f"continuity faithfulness ({label}): {sum(scored) / len(scored):.2f} ({sum(scored):.0f}/{len(scored)})")


def main() -> None:
    """Score the baseline module, run BootstrapFewShot, score the result, then save it."""
    lm = dspy.LM("together_ai/deepseek-ai/DeepSeek-V4-Flash-0731", api_key=TOGETHER_API_KEY, max_tokens=4096)
    dspy.configure(lm=lm)

    eval_set = build_eval_set(load_eval_articles(), batch_size=18) + build_continuity_eval_set(
        load_continuity_eval_cases(), reference_date=date.today()
    )
    print(f"eval set: {len(eval_set)} examples")

    baseline = DigestGenerator()
    baseline_score, baseline_passes, baseline_texts = evaluate(baseline, eval_set)
    print(f"baseline compliance: {baseline_score:.2f}")
    for rule, count in baseline_passes.items():
        print(f"  {rule}: {count}/{len(eval_set)} passed")
    report_continuity_faithfulness("baseline, synthetic cases", eval_set, baseline_texts)

    optimizer = BootstrapFewShot(
        metric=digest_compliance_score,
        metric_threshold=1.0,
        max_bootstrapped_demos=2,
        max_labeled_demos=2,
    )
    optimized = optimizer.compile(DigestGenerator(), trainset=eval_set)
    optimized_score, optimized_passes, optimized_texts = evaluate(optimized, eval_set)
    print(f"optimized compliance: {optimized_score:.2f}")
    for rule, count in optimized_passes.items():
        print(f"  {rule}: {count}/{len(eval_set)} passed")
    report_continuity_faithfulness("optimized, synthetic cases", eval_set, optimized_texts)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    optimized.save(str(COMPILED_PROGRAM_PATH))
    print(f"saved compiled program to {COMPILED_PROGRAM_PATH}")

    if not EVAL_CONTINUITY_CONTEXT_PATH.exists():
        print(
            f"skipping exa corroboration check: {EVAL_CONTINUITY_CONTEXT_PATH} not found "
            "(run `invoke fetch-eval-continuity-context` first)"
        )
        return

    # Checks retrieval (is the embedding match independently corroborated on the real web)
    # and generation (did the model frame it faithfully) together, against real content the
    # synthetic cases above can't provide - runs once, doesn't depend on baseline/optimized.
    real_continuity_set = build_real_continuity_eval_set(
        load_eval_articles(), load_eval_continuity_context(), reference_date=date.today()
    )
    print(f"real continuity eval set: {len(real_continuity_set)} examples")
    if real_continuity_set:
        real_texts = [optimized(**example.inputs()).digest for example in real_continuity_set]
        corroboration_scores = [exa_corroboration_score(example, None) for example in real_continuity_set]
        print(
            f"exa corroboration: {sum(corroboration_scores) / len(corroboration_scores):.2f} "
            f"({sum(corroboration_scores):.0f}/{len(corroboration_scores)})"
        )
        report_continuity_faithfulness("real batches", real_continuity_set, real_texts)


if __name__ == "__main__":
    main()
