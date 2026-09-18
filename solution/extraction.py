"""The three Gaps, complete. Compare with `starter/extraction.py` when you are stuck."""

import asyncio
from collections.abc import Collection

from app.drafts import Draft, ExtractionFailed, Fallback, Problem, RejectedDraft
from app.provider import Provider, ProviderError, ProviderServerError
from app.units import TO_TASTE

# Only failures that may go away on a second try are retried.
RETRYABLE = (TimeoutError, ProviderServerError)


# Gap 1
def validate_draft(draft: Draft, units: Collection[str]) -> list[Problem]:
    problems: list[Problem] = []
    if not draft.recipe_name.strip():
        problems.append(Problem("recipe_name", "Recipe name is empty."))
    if draft.prep_time_minutes is not None and draft.prep_time_minutes < 0:
        problems.append(Problem("prep_time_minutes", "Prep time cannot be negative."))
    if not draft.ingredients:
        problems.append(Problem("ingredients", "The Draft has no ingredients."))

    for i, ingredient in enumerate(draft.ingredients):
        path = f"ingredients[{i}]"
        if not ingredient.name.strip():
            problems.append(Problem(f"{path}.name", "Ingredient name is empty."))
        if ingredient.unit not in units:
            problems.append(Problem(f"{path}.unit", f"'{ingredient.unit}' is not an allowed Unit."))
        if ingredient.unit == TO_TASTE:
            if ingredient.amount is not None:
                problems.append(Problem(f"{path}.amount", f"{TO_TASTE} has no Amount."))
        elif ingredient.amount is None:
            problems.append(Problem(f"{path}.amount", "Amount is missing."))
        elif ingredient.amount <= 0:
            problems.append(Problem(f"{path}.amount", "Amount must be more than 0."))
    return problems


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
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            draft = await asyncio.wait_for(provider.extract(recipe_text), timeout)
        except RETRYABLE as exc:
            last_error = exc
            if attempt < attempts:
                await asyncio.sleep(backoff)
            continue
        except ProviderError as exc:
            raise ExtractionFailed(str(exc)) from exc

        # A Rejected Draft is an answer, not a failure: show it to a person, never retry it.
        problems = validate_draft(draft, units)
        if problems:
            return RejectedDraft(draft=draft, problems=problems)
        return draft

    if isinstance(last_error, TimeoutError):
        reason = f"The model did not answer within {timeout:g} seconds ({attempts} attempts)."
    else:
        reason = f"{last_error} Tried {attempts} times."
    raise ExtractionFailed(reason) from last_error


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
    try:
        return await extract(
            recipe_text, provider, units, timeout=timeout, attempts=attempts, backoff=backoff
        )
    except ExtractionFailed as exc:
        return Fallback(recipe_text=recipe_text, reason=exc.reason)
