import dspy


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
    - Weaves in a few relevant hashtags like #Zambia, #ZambianNews, or story-specific
      ones, but does NOT just list them at the end
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


def generate_facebook_post(digest: str, date: str, time_context: str, link: str) -> str:
    """Generate Facebook post text from a news digest using a DSPy module."""
    return FacebookPostGenerator()(digest=digest, date=date, time_context=time_context, link=link).post


def generate_image_concept(digest: str) -> str:
    """Generate a promotional image concept from a news digest using a DSPy module."""
    return ImageConceptGenerator()(digest=digest).concept
