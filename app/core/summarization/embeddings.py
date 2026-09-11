import requests

from app.core.utilities import OPENROUTER_API_KEY

EMBEDDING_MODEL = "baai/bge-m3"

# bge-m3's real context cap is 8192 tokens (confirmed via a live 400 from
# OpenRouter, not the docs page). Binary-searched the real chars/token ratio
# on a real dense article (article 1171): ~3.99 chars/token, no margin - so
# 3.5 chars/token leaves real headroom instead of assuming the usual ~4.
_MAX_EMBEDDING_CHARS = int(8192 * 3.5)


def embed_text(content: str) -> list[float] | None:
    """Embed text via OpenRouter's bge-m3 model, for story-continuity similarity search.

    Returns None for empty/whitespace-only content without calling the API -
    OpenRouter's /v1/embeddings rejects an empty-string input with a 400.
    Longer articles are truncated to bge-m3's 8192-token context window.
    """
    return embed_texts([content])[0]


def embed_texts(contents: list[str]) -> list[list[float] | None]:
    """Batch version of `embed_text` - one OpenRouter call for many articles.

    For bulk backfills: collapses N HTTP round-trips into one. Empty/whitespace
    entries are excluded from the request (same as `embed_text`) and come back
    as None at their original position.
    """
    indices = [i for i, c in enumerate(contents) if c.strip()]
    if not indices:
        return [None] * len(contents)

    response = requests.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        json={
            "model": EMBEDDING_MODEL,
            "input": [contents[i][:_MAX_EMBEDDING_CHARS] for i in indices],
        },
        timeout=60,
    )
    response.raise_for_status()

    results: list[list[float] | None] = [None] * len(contents)
    for item in response.json()["data"]:
        results[indices[item["index"]]] = item["embedding"]
    return results
