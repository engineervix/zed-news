import logging

import cohere

from app.core.utilities import COHERE_API_KEY

co = cohere.Client(COHERE_API_KEY)


def summarize(content: str, title: str) -> str:
    """Summarize the content using Cohere's summarization API.

    https://docs.cohere.com/reference/summarize-2
    """

    logging.info(f"Summarizing '{title}' via Cohere ...")
    response = co.summarize(
        text=content,
        model="summarize-xlarge",
        temperature=0,
        length="auto",
        format="paragraph",
        extractiveness="auto",
        additional_command="in a manner suitable for reading as part of a podcast",
    )
    return response.summary
