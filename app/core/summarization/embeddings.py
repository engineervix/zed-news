import requests

from app.core.utilities import OPENROUTER_API_KEY

EMBEDDING_MODEL = "baai/bge-m3"


def embed_text(content: str) -> list[float] | None:
    """Embed text via OpenRouter's bge-m3 model, for story-continuity similarity search.

    Returns None for empty/whitespace-only content without calling the API -
    OpenRouter's /v1/embeddings rejects an empty-string input with a 400.
    """
    if not content.strip():
        return None

    response = requests.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        json={"model": EMBEDDING_MODEL, "input": content},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]
