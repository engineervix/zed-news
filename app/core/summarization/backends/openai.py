import logging

from langchain import OpenAI, PromptTemplate

from app.core.utilities import OPENAI_API_KEY

llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)


def summarize(content: str, title: str) -> str:
    """Summarize the content using OpenAI's language model."""

    template = """
    Please provide a very short, sweet, informative and engaging summary of the following news entry, in not more than two sentences.
    Please provide your output in a manner suitable for reading as part of a podcast.

    {entry}
    """

    prompt = PromptTemplate(input_variables=["entry"], template=template)
    summary_prompt = prompt.format(entry=content)

    num_tokens = llm.get_num_tokens(summary_prompt)
    logging.info(f"'{title}' and its prompt has {num_tokens} tokens")

    return llm(summary_prompt)
