"""Run BootstrapFewShot against post.py's two signatures and compare to the baseline.

Dev-only: hits the real Together model, costs real API calls. Run with
`invoke optimize-social`. Saves the compiled programs (gitignored, same
policy as the eval fixtures: real generated content, not committed).
"""

import dspy
from dspy.teleprompt import BootstrapFewShot

from app.core.summarization.post import (
    FACEBOOK_POST_COMPILED_PROGRAM_PATH,
    FACEBOOK_POST_COMPLIANCE_RULES,
    IMAGE_CONCEPT_COMPILED_PROGRAM_PATH,
    IMAGE_CONCEPT_COMPLIANCE_RULES,
    FacebookPostGenerator,
    ImageConceptGenerator,
    build_facebook_post_eval_set,
    build_image_concept_eval_set,
    facebook_post_compliance_score,
    image_concept_compliance_score,
    load_eval_digests,
)
from app.core.utilities import TOGETHER_API_KEY


def evaluate(module: dspy.Module, eval_set: list[dspy.Example], score, rules: dict, output_field: str):
    """Score a module's generations against the eval set, rule by rule."""
    preds = [module(**example.inputs()) for example in eval_set]
    scores = [score(None, pred) for pred in preds]
    passes = {name: sum(check(getattr(pred, output_field)) for pred in preds) for name, check in rules.items()}
    return sum(scores) / len(scores), passes


def run(name: str, module_cls, eval_set, score, rules, output_field, program_path) -> None:
    """Score baseline, run BootstrapFewShot, score result, then save the compiled program."""
    baseline = module_cls()
    baseline_score, baseline_passes = evaluate(baseline, eval_set, score, rules, output_field)
    print(f"{name} baseline compliance: {baseline_score:.2f}")
    for rule, count in baseline_passes.items():
        print(f"  {rule}: {count}/{len(eval_set)} passed")

    optimizer = BootstrapFewShot(
        metric=score,
        metric_threshold=1.0,
        max_bootstrapped_demos=2,
        max_labeled_demos=2,
    )
    optimized = optimizer.compile(module_cls(), trainset=eval_set)
    optimized_score, optimized_passes = evaluate(optimized, eval_set, score, rules, output_field)
    print(f"{name} optimized compliance: {optimized_score:.2f}")
    for rule, count in optimized_passes.items():
        print(f"  {rule}: {count}/{len(eval_set)} passed")

    program_path.parent.mkdir(parents=True, exist_ok=True)
    optimized.save(str(program_path))
    print(f"saved compiled {name} program to {program_path}")


def main() -> None:
    lm = dspy.LM("together_ai/deepseek-ai/DeepSeek-V4-Flash-0731", api_key=TOGETHER_API_KEY, max_tokens=4096)
    dspy.configure(lm=lm)

    digests = load_eval_digests()

    facebook_post_eval_set = build_facebook_post_eval_set(digests)
    print(f"facebook post eval set: {len(facebook_post_eval_set)} examples")
    run(
        "facebook post",
        FacebookPostGenerator,
        facebook_post_eval_set,
        facebook_post_compliance_score,
        FACEBOOK_POST_COMPLIANCE_RULES,
        "post",
        FACEBOOK_POST_COMPILED_PROGRAM_PATH,
    )

    image_concept_eval_set = build_image_concept_eval_set(digests)
    print(f"image concept eval set: {len(image_concept_eval_set)} examples")
    run(
        "image concept",
        ImageConceptGenerator,
        image_concept_eval_set,
        image_concept_compliance_score,
        IMAGE_CONCEPT_COMPLIANCE_RULES,
        "concept",
        IMAGE_CONCEPT_COMPILED_PROGRAM_PATH,
    )


if __name__ == "__main__":
    main()
