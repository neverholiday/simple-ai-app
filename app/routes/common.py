"""Helpers shared by the route modules."""

from collections.abc import Iterator

from fastapi import Request
from fastapi.responses import HTMLResponse

from app import db
from app.drafts import Draft
from app.recipes import RecipeInput

BLANK_ROWS = 3


def get_conn(request: Request) -> Iterator:
    conn = db.connect(request.app.state.settings.db_path)
    try:
        yield conn
    finally:
        conn.close()


def render(request: Request, name: str, context: dict, status_code: int = 200) -> HTMLResponse:
    return request.app.state.templates.TemplateResponse(
        request, name, context, status_code=status_code
    )


def format_amount(amount: float | None) -> str:
    if amount is None:
        return ""
    return f"{amount:g}"


def form_values(source: RecipeInput | Draft | None) -> dict:
    """Turn a saved recipe, submitted input or Draft into values for the recipe form."""
    if source is None:
        name, prep, ingredients = "", None, []
    elif isinstance(source, Draft):
        name, prep, ingredients = source.recipe_name, source.prep_time_minutes, source.ingredients
    else:
        name, prep, ingredients = source.name, source.prep_time_minutes, source.ingredients

    rows = [
        {"name": ing.name, "amount": format_amount(ing.amount), "unit": ing.unit}
        for ing in ingredients
    ]
    rows += [{"name": "", "amount": "", "unit": ""} for _ in range(BLANK_ROWS)]
    return {"name": name, "prep_time_minutes": "" if prep is None else prep, "rows": rows}
