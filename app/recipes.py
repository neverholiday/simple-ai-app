"""Recipes: the deterministic CRUD core.

Manual Entry, edit and Review all save through `parse_form`, `validate_recipe`
and `create_recipe` / `update_recipe`. How the values got into the form does
not matter here.
"""

import sqlite3
from collections.abc import Collection
from dataclasses import dataclass, field

from app.units import TO_TASTE


@dataclass
class IngredientInput:
    name: str
    amount: float | None
    unit: str


@dataclass
class RecipeInput:
    name: str
    prep_time_minutes: int | None
    ingredients: list[IngredientInput] = field(default_factory=list)


@dataclass
class Recipe(RecipeInput):
    id: int = 0
    created_at: str = ""
    updated_at: str = ""


def _parse_number(raw: str) -> float:
    raw = raw.strip()
    if "/" in raw:
        top, bottom = raw.split("/", 1)
        return float(top) / float(bottom)
    return float(raw)


def parse_form(form) -> tuple[RecipeInput, dict[str, str]]:
    """Read the submitted recipe form. Returns the values and any parse errors by field."""
    errors: dict[str, str] = {}

    prep_raw = (form.get("prep_time_minutes") or "").strip()
    prep_time: int | None = None
    if prep_raw:
        try:
            prep_time = int(prep_raw)
        except ValueError:
            errors["prep_time_minutes"] = "Prep time must be a whole number of minutes."

    names = form.getlist("ingredient_name")
    amounts = form.getlist("ingredient_amount")
    units = form.getlist("ingredient_unit")

    ingredients: list[IngredientInput] = []
    for name, amount_raw, unit in zip(names, amounts, units, strict=False):
        if not name.strip() and not amount_raw.strip():
            continue  # a blank row
        index = len(ingredients)
        amount: float | None = None
        if amount_raw.strip():
            try:
                amount = _parse_number(amount_raw)
            except (ValueError, ZeroDivisionError):
                errors[f"ingredients[{index}].amount"] = "Amount must be a number, like 2 or 1/2."
        ingredients.append(IngredientInput(name=name.strip(), amount=amount, unit=unit))

    recipe = RecipeInput(
        name=(form.get("name") or "").strip(),
        prep_time_minutes=prep_time,
        ingredients=ingredients,
    )
    return recipe, errors


def validate_recipe(recipe: RecipeInput, units: Collection[str]) -> dict[str, str]:
    """Check the recipe rules. Returns error messages by field; empty means valid."""
    errors: dict[str, str] = {}
    if not recipe.name:
        errors["name"] = "Recipe name is required."
    if recipe.prep_time_minutes is not None and recipe.prep_time_minutes < 0:
        errors["prep_time_minutes"] = "Prep time cannot be negative."
    if not recipe.ingredients:
        errors["ingredients"] = "Add at least one ingredient."

    for i, ingredient in enumerate(recipe.ingredients):
        path = f"ingredients[{i}]"
        if not ingredient.name:
            errors[f"{path}.name"] = "Ingredient name is required."
        if not ingredient.unit:
            errors[f"{path}.unit"] = "Choose a Unit."
        elif ingredient.unit not in units:
            errors[f"{path}.unit"] = f"'{ingredient.unit}' is not an allowed Unit."
        if ingredient.unit == TO_TASTE:
            if ingredient.amount is not None:
                errors[f"{path}.amount"] = f"{TO_TASTE} has no Amount. Leave it empty."
        elif ingredient.amount is None:
            errors[f"{path}.amount"] = "Amount is required."
        elif ingredient.amount <= 0:
            errors[f"{path}.amount"] = "Amount must be more than 0."
    return errors


def list_recipes(conn: sqlite3.Connection) -> list[Recipe]:
    rows = conn.execute("SELECT id FROM recipes ORDER BY updated_at DESC, id DESC").fetchall()
    return [recipe for row in rows if (recipe := get_recipe(conn, row["id"])) is not None]


def get_recipe(conn: sqlite3.Connection, recipe_id: int) -> Recipe | None:
    row = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    if row is None:
        return None
    ingredient_rows = conn.execute(
        "SELECT name, amount, unit FROM ingredients WHERE recipe_id = ? ORDER BY position",
        (recipe_id,),
    ).fetchall()
    return Recipe(
        id=row["id"],
        name=row["name"],
        prep_time_minutes=row["prep_time_minutes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        ingredients=[
            IngredientInput(name=r["name"], amount=r["amount"], unit=r["unit"])
            for r in ingredient_rows
        ],
    )


def create_recipe(conn: sqlite3.Connection, recipe: RecipeInput) -> int:
    with conn:
        cursor = conn.execute(
            "INSERT INTO recipes (name, prep_time_minutes) VALUES (?, ?)",
            (recipe.name, recipe.prep_time_minutes),
        )
        recipe_id = cursor.lastrowid
        _insert_ingredients(conn, recipe_id, recipe.ingredients)
    return recipe_id


def update_recipe(conn: sqlite3.Connection, recipe_id: int, recipe: RecipeInput) -> bool:
    with conn:
        cursor = conn.execute(
            "UPDATE recipes SET name = ?, prep_time_minutes = ?, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = ?",
            (recipe.name, recipe.prep_time_minutes, recipe_id),
        )
        if cursor.rowcount == 0:
            return False
        conn.execute("DELETE FROM ingredients WHERE recipe_id = ?", (recipe_id,))
        _insert_ingredients(conn, recipe_id, recipe.ingredients)
    return True


def delete_recipe(conn: sqlite3.Connection, recipe_id: int) -> bool:
    with conn:
        cursor = conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    return cursor.rowcount > 0


def _insert_ingredients(
    conn: sqlite3.Connection, recipe_id: int, ingredients: list[IngredientInput]
) -> None:
    conn.executemany(
        "INSERT INTO ingredients (recipe_id, position, name, amount, unit) VALUES (?, ?, ?, ?, ?)",
        [(recipe_id, i, ing.name, ing.amount, ing.unit) for i, ing in enumerate(ingredients)],
    )
