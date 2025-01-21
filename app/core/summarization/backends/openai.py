import logging
import math
import textwrap

from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI

from app.core.utilities import OPENAI_API_KEY

llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
MAX_TOKENS = 4096


def summarize(content: str, title: str) -> str:
    """Summarize the content using OpenAI's language model."""

    template = """
    Please provide a very short, sweet, informative and engaging summary of the following news entry, in not more than two sentences.
    Please provide your output in a manner suitable for reading as part of a podcast.

    {entry}
    """

    # Calculate the maximum number of tokens available for the prompt
    max_prompt_tokens = MAX_TOKENS - llm.get_num_tokens(template)

    # Trim the content if it exceeds the available tokens
    # TODO: Instead of truncating the content, split it
    # see <https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/split_by_token>
    chars = int(max_prompt_tokens * 3.75)  # Assuming 1 token ≈ 4 chars
    # round down max_chars to the nearest 100
    max_chars = math.floor(chars / 100) * 100
    if len(content) > max_chars:
        content = textwrap.shorten(content, width=max_chars, placeholder=" ...")

    prompt = PromptTemplate(input_variables=["entry"], template=template)

    summary_prompt = prompt.format(entry=content)

    num_tokens = llm.get_num_tokens(summary_prompt)
    logging.info(f"'{title}' and its prompt has {num_tokens} tokens")

    return llm(summary_prompt)
