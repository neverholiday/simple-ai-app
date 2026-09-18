"""The three Gaps you write. Do them in order: 1, then 2, then 3.

Run the tests for one Gap at a time:

    uv run pytest tests/test_gap1_validate.py

Everything you need is imported below. When all tests pass, start the app with
`--use starter` and flip the Demo Switches to watch your code handle them.
"""

import asyncio  # noqa: F401  (you will need it in Gap 2)
from collections.abc import Collection

from app.drafts import Draft, ExtractionFailed, Fallback, Problem, RejectedDraft  # noqa: F401
from app.provider import Provider, ProviderError, ProviderServerError  # noqa: F401
from app.units import TO_TASTE  # noqa: F401


# Gap 1
def validate_draft(draft: Draft, units: Collection[str]) -> list[Problem]:
    """Check a Draft against the recipe rules and return every Problem found.

    The JSON from the model is already well-formed. It can still be wrong.

    Return one Problem for each of these (an empty list means the Draft is valid):
    - `recipe_name` is empty or only spaces.       field: "recipe_name"
    - `prep_time_minutes` is negative.              field: "prep_time_minutes"
    - there are no ingredients.                     field: "ingredients"
    For each ingredient i:
    - its name is empty.                            field: "ingredients[i].name"
    - its unit is not in `units`.                   field: "ingredients[i].unit"
      Put the wrong unit in the message, for example "'ทัพพี' is not an allowed Unit."
    - its unit is TO_TASTE and it has an amount.    field: "ingredients[i].amount"
    - its unit is not TO_TASTE and amount is None.  field: "ingredients[i].amount"
    - its amount is 0 or less.                      field: "ingredients[i].amount"

    List every Problem, not just the first one.
    """
    raise NotImplementedError("Gap 1: validate_draft is not written yet.")


# Gap 2
async def extract(
    recipe_text: str,
    provider: Provider,
    units: Collection[str],
    *,
    timeout: float = 6.0,
    attempts: int = 2,
    backoff: float = 0.5,
) -> Draft | RejectedDraft:
    """Ask the model for a Draft, with a timeout on each attempt and a retry.

    - Call `provider.extract(recipe_text)`. Give each attempt at most `timeout` seconds
      (`asyncio.wait_for` raises `TimeoutError` when time runs out).
    - Make at most `attempts` attempts. Wait `backoff` seconds before trying again.
    - Retry only `TimeoutError` and `ProviderServerError`: they may work next time.
    - Any other `ProviderError` will not get better by retrying: raise
      `ExtractionFailed` straight away, with a reason a person can read.
    - When every attempt failed, raise `ExtractionFailed` with the reason.
    - When a Draft comes back, check it with `validate_draft` (Gap 1).
      If there are problems, return `RejectedDraft(draft=..., problems=...)`.
      Never retry a Rejected Draft: a person fixes it during Review.
      Otherwise return the Draft.
    """
    raise NotImplementedError("Gap 2: extract is not written yet.")


# Gap 3
async def extract_or_fallback(
    recipe_text: str,
    provider: Provider,
    units: Collection[str],
    *,
    timeout: float = 6.0,
    attempts: int = 2,
    backoff: float = 0.5,
) -> Draft | RejectedDraft | Fallback:
    """Always give the person something to work with, never an error page.

    - Return whatever `extract` (Gap 2) returns: a Draft or a Rejected Draft.
      Pass `timeout`, `attempts` and `backoff` through.
    - If `extract` raises `ExtractionFailed`, return
      `Fallback(recipe_text=recipe_text, reason=...)` using the reason from the error,
      so the person keeps their text and can fill in the form by hand.
    """
    raise NotImplementedError("Gap 3: extract_or_fallback is not written yet.")
