from datetime import date

import requests

from app.core.utilities import EXA_API_KEY

# Exa's real news index does cover Zambian outlets
# (znbc.co.zm, times.co.zm, daily-mail.co.zm all returned real, dated results), and
# date-only ISO strings ("YYYY-MM-DD") are accepted for startPublishedDate/endPublishedDate.
EXA_SEARCH_URL = "https://api.exa.ai/search"


def exa_search(query: str, start_date: date, end_date: date, num_results: int = 1) -> list[dict]:
    """Search Exa's real web index for independent corroboration of a topic.

    Eval-only - never called from production digest generation, only from
    `exa_corroboration_score` during optimize/eval runs, which only checks whether
    any result exists - `num_results` defaults to 1 accordingly, override for a
    caller that actually inspects multiple results. Restricted to `category="news"`
    and the given date range so a match actually falls within the timeframe a
    continuity claim is about, not just anywhere on the web. Returns [] without
    calling the API when `EXA_API_KEY` isn't configured - this is an informational
    metric, a missing key shouldn't crash the whole eval run.
    """
    if not EXA_API_KEY:
        return []

    response = requests.post(
        EXA_SEARCH_URL,
        headers={"x-api-key": EXA_API_KEY},
        json={
            "query": query,
            "numResults": num_results,
            "category": "news",
            "startPublishedDate": start_date.isoformat(),
            "endPublishedDate": end_date.isoformat(),
        },
        timeout=30,
        # requests strips Authorization on a cross-host redirect, but not custom
        # headers - a redirect from Exa's own endpoint would otherwise carry
        # EXA_API_KEY to wherever it points. No legitimate reason for this call
        # to be redirected at all.
        allow_redirects=False,
    )
    response.raise_for_status()
    return response.json()["results"]
