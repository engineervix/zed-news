import logging

import together

from app.core.utilities import TOGETHER_API_KEY

together.api_key = TOGETHER_API_KEY


def summarize(content: str, title: str) -> str:
    """
    Summarize the content using Together AI's Inference API.

    https://docs.together.ai/reference/complete
    """

    prompt = f"<human>: You are a distinguished news editor and content publisher, your task is to summarize the following news entry. The summary should accurately reflect the main message and arguments presented in the original text, while also being concise and easy to understand.\n\n ```{content}```\n<bot>:"
    model = "togethercomputer/llama-2-70b-chat"
    temperature = 0.7
    max_tokens = 512

    output = together.Complete.create(
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    logging.info(output)

    return output["output"]["choices"][0]["text"]