import logging
import time

from together import Together

from app.core.utilities import TOGETHER_API_KEY

client = Together(api_key=TOGETHER_API_KEY)


def summarize(content: str, title: str) -> str:
    """
    Summarize the content using Together AI's Inference API.

    https://docs.together.ai/reference/complete
    """

    prompt = f"You are a distinguished news editor and content publisher, your task is to summarize the following news entry. The summary should accurately reflect the main message and arguments presented in the original news entry, while also being concise and easy to understand. Your summary should not exceed two sentences.\n\n ```{content}```:"
    model = "garage-bAInd/Platypus2-70B-instruct"
    temperature = 0.7
    max_tokens = 192

    response = client.completions.create(
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    time.sleep(1.5)
    logging.info(response)

    return response.choices[0].text


def brief_summary(content: str, title: str) -> str:
    """
    Very brief summary of the content using Together AI's Inference API.

    https://docs.together.ai/reference/complete
    """

    prompt = f"You are a distinguished news editor and content publisher, your task is to summarize the following news entry in one sentence.\n\n ```{content}```:"
    model = "garage-bAInd/Platypus2-70B-instruct"
    temperature = 0.7
    max_tokens = 96

    response = client.completions.create(
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    time.sleep(1.5)
    logging.info(response)

    return response.choices[0].text
