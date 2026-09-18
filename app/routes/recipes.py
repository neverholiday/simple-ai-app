"""CRUD for Recipes. Manual Entry, edit and Review all save through here."""

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from app import recipes
from app.routes.common import form_values, get_conn, render
from app.units import UNIT_NAMES

router = APIRouter()

Conn = Annotated[sqlite3.Connection, Depends(get_conn)]


@router.get("/recipes")
def list_page(request: Request, conn: Conn):
    return render(request, "recipe_list.html", {"recipes": recipes.list_recipes(conn)})


@router.get("/recipes/new")
def new_page(request: Request):
    return render(
        request,
        "recipe_form.html",
        {
            "title": "New recipe",
            "action": "/recipes",
            "mode": "manual",
            "values": form_values(None),
            "errors": {},
        },
    )


@router.post("/recipes")
async def create(request: Request, conn: Conn):
    form = await request.form()
    recipe, errors = recipes.parse_form(form)
    errors = {**recipes.validate_recipe(recipe, UNIT_NAMES), **errors}
    if errors:
        return _form_with_errors(request, form, recipe, errors, action="/recipes")
    recipe_id = recipes.create_recipe(conn, recipe)
    return RedirectResponse(f"/recipes/{recipe_id}", status_code=303)


@router.get("/recipes/{recipe_id}")
def detail_page(request: Request, recipe_id: int, conn: Conn):
    recipe = recipes.get_recipe(conn, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return render(request, "recipe_detail.html", {"recipe": recipe})


@router.get("/recipes/{recipe_id}/edit")
def edit_page(request: Request, recipe_id: int, conn: Conn):
    recipe = recipes.get_recipe(conn, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return render(
        request,
        "recipe_form.html",
        {
            "title": f"Edit {recipe.name}",
            "action": f"/recipes/{recipe_id}",
            "mode": "edit",
            "values": form_values(recipe),
            "errors": {},
        },
    )


@router.post("/recipes/{recipe_id}")
async def update(request: Request, recipe_id: int, conn: Conn):
    form = await request.form()
    recipe, errors = recipes.parse_form(form)
    errors = {**recipes.validate_recipe(recipe, UNIT_NAMES), **errors}
    if errors:
        return _form_with_errors(request, form, recipe, errors, action=f"/recipes/{recipe_id}")
    if not recipes.update_recipe(conn, recipe_id, recipe):
        raise HTTPException(status_code=404, detail="Recipe not found")
    return RedirectResponse(f"/recipes/{recipe_id}", status_code=303)


@router.post("/recipes/{recipe_id}/delete")
def delete(recipe_id: int, conn: Conn):
    if not recipes.delete_recipe(conn, recipe_id):
        raise HTTPException(status_code=404, detail="Recipe not found")
    return RedirectResponse("/recipes", status_code=303)


def _form_with_errors(request, form, recipe, errors, action):
    # A failed save from Review stays in Review: the Recipe Text stays beside the form.
    mode = form.get("mode") or "manual"
    return render(
        request,
        "recipe_form.html",
        {
            "title": "Fix the recipe",
            "action": action,
            "mode": mode,
            "values": form_values(recipe),
            "errors": errors,
            "recipe_text": form.get("recipe_text") or "",
        },
        status_code=422,
    )
