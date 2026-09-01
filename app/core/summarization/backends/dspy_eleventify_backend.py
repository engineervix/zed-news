import dspy


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


def generate_digest_description(digest: str) -> str:
    """Generate a brief digest description from a news digest using a DSPy module."""
    return DigestDescriptionGenerator()(digest=digest).description
