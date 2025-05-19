import logging
import re
import sys
import time

from together import Together, error

from app.core.utilities import TOGETHER_API_KEY

client = Together(api_key=TOGETHER_API_KEY)


def summarize(content: str, title: str) -> str:
    """
    TODO: rename this function to `synthesize`
    Synthesize the content using Together AI's Inference API.

    This goes beyond summarization to extract key insights and context
    that will be valuable when combined with other news items.

    https://docs.together.ai/reference/complete
    """

    system_prompt = "You are a distinguished news analyst and content synthesizer. Your task is to distill the provided news entry into its essential elements while preserving its context and significance. Focus on extracting what makes this news item meaningful in the broader information landscape."

    user_prompt = f"Synthesize the following news entry in a few sentences sentences. Highlight the core information and its relevance or implications, rather than just summarizing facts.\n\n```{content}```"

    model = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    # NOTE: free models tend to have unpredictable rate-limits
    # model = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
    # model = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"
    temperature = 0.7
    max_tokens = 384

    retries = 0
    max_retries = 30  # 10 seconds x 30 times is approx 5 minutes

    while retries < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            time.sleep(1.5)
            logging.info(completion)

            if result := completion.choices[0].message.content.strip():
                result = result.replace("```", "")  # Remove triple backticks
                first_line = result.splitlines()[0].lower()
                unwanted = ["summary:", "here's", "here is", "sure"]

                if any(string in first_line for string in unwanted):
                    # Remove the first line from result
                    result = "\n".join(result.split("\n")[1:])

                result_with_no_linebreaks = result.replace("\n", "")  # Remove newlines

                # Remove everything between <think> and </think> tags
                return re.sub(r"<think>.*?</think>", "", result_with_no_linebreaks, flags=re.DOTALL)

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

    system_prompt = "You are a distinguished news editor and content publisher. Your task is to summarize the provided news entry. The summary should accurately reflect the main message and arguments presented in the original news entry, while also being concise and easy to understand."

    user_prompt = f"Summarize the following news entry in one sentence.\n\n ```{content}```"

    model = "meta-llama/Meta-Llama-3-70B-Instruct-Turbo"
    temperature = 0.7
    max_tokens = 96

    retries = 0
    max_retries = 30  # 10 seconds x 30 times is approx 5 minutes

    while retries < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            time.sleep(1.5)
            logging.info(completion)

            if result := completion.choices[0].message.content.strip():
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
