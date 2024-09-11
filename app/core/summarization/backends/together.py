import logging
import time
import sys

from together import Together, error

from app.core.utilities import TOGETHER_API_KEY

client = Together(api_key=TOGETHER_API_KEY)


def summarize(content: str, title: str) -> str:
    """
    Summarize the content using Together AI's Inference API.

    https://docs.together.ai/reference/complete
    """

    prompt = f"You are a distinguished news editor and content publisher, your task is to summarize the following news entry. The summary should accurately reflect the main message and arguments presented in the original news entry, while also being concise and easy to understand. Your summary should not exceed two sentences.\n\n ```{content}```:"
    model = "mistralai/Mixtral-8x22B-Instruct-v0.1"
    temperature = 0.7
    max_tokens = 192

    retries = 0
    max_retries = 30  # 10 seconds x 30 times is approx 5 minutes

    while retries < max_retries:
        try:
            response = client.completions.create(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            time.sleep(1.5)
            logging.info(response)

            if result := response.choices[0].text.strip():
                result = result.replace("```", "")  # Remove triple backticks
                first_line = result.splitlines()[0].lower()
                unwanted = ["summary:", "here's", "here is", "sure"]

                if any(string in first_line for string in unwanted):
                    # Remove the first line from result
                    result = "\n".join(result.split("\n")[1:])

                return result.replace("\n", "")  # Remove newlines
        except error.ServiceUnavailableError:
            retries += 1
            logging.error(f"Service unavailable. Retrying {retries}/{max_retries} in 10 seconds...")
            time.sleep(10)

    # If we exhausted the retries, give up
    logging.error(f"Failed after {max_retries} attempts.")
    sys.exit(1)


def brief_summary(content: str, title: str) -> str:
    """
    Very brief summary of the content using Together AI's Inference API.

    https://docs.together.ai/reference/complete
    """

    prompt = f"You are a distinguished news editor and content publisher, your task is to summarize the following news entry in one sentence.\n\n ```{content}```:"
    model = "mistralai/Mixtral-8x7B-v0.1"
    temperature = 0.7
    max_tokens = 96

    retries = 0
    max_retries = 30  # 10 seconds x 30 times is approx 5 minutes

    while retries < max_retries:
        try:
            response = client.completions.create(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            time.sleep(1.5)
            logging.info(response)

            return response.choices[0].text
        except error.ServiceUnavailableError:
            retries += 1
            logging.error(f"Service unavailable. Retrying {retries}/{max_retries} in 10 seconds...")
            time.sleep(10)

    # If we exhausted the retries, give up
    logging.error(f"Failed after {max_retries} attempts.")
    sys.exit(1)
