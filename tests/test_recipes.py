import sqlite3

import pytest
from starlette.datastructures import FormData

from app import db, recipes
from app.recipes import IngredientInput, RecipeInput
from app.units import UNIT_NAMES


@pytest.fixture
def conn(tmp_path):
    connection = db.connect(tmp_path / "recipes.db")
    db.init_db(connection)
    yield connection
    connection.close()


def a_recipe(**overrides) -> RecipeInput:
    values = {
        "name": "น้ำพริกกะปิ",
        "prep_time_minutes": 15,
        "ingredients": [
            IngredientInput(name="กะปิ", amount=1, unit="ช้อนโต๊ะ"),
            IngredientInput(name="น้ำตาลปี๊บ", amount=None, unit="ตามชอบ"),
        ],
    }
    values.update(overrides)
    return RecipeInput(**values)


def test_create_get_update_delete(conn):
    recipe_id = recipes.create_recipe(conn, a_recipe())
    saved = recipes.get_recipe(conn, recipe_id)
    assert saved.name == "น้ำพริกกะปิ"
    assert [i.unit for i in saved.ingredients] == ["ช้อนโต๊ะ", "ตามชอบ"]
    assert saved.ingredients[1].amount is None

    changed = a_recipe(name="น้ำพริกกะปิ สูตรเผ็ด", ingredients=[IngredientInput("พริก", 20, "เม็ด")])
    assert recipes.update_recipe(conn, recipe_id, changed)
    saved = recipes.get_recipe(conn, recipe_id)
    assert saved.name == "น้ำพริกกะปิ สูตรเผ็ด"
    assert len(saved.ingredients) == 1

    assert [r.id for r in recipes.list_recipes(conn)] == [recipe_id]
    assert recipes.delete_recipe(conn, recipe_id)
    assert recipes.get_recipe(conn, recipe_id) is None
    assert conn.execute("SELECT COUNT(*) FROM ingredients").fetchone()[0] == 0


def test_update_or_delete_missing_recipe_returns_false(conn):
    assert not recipes.update_recipe(conn, 999, a_recipe())
    assert not recipes.delete_recipe(conn, 999)


def test_foreign_keys_are_really_on(conn):
    """The database refuses an unknown Unit even when validation is skipped."""
    with pytest.raises(sqlite3.IntegrityError):
        recipes.create_recipe(
            conn, a_recipe(ingredients=[IngredientInput(name="ข้าว", amount=2, unit="ทัพพี")])
        )


def test_valid_recipe_has_no_errors():
    assert recipes.validate_recipe(a_recipe(), UNIT_NAMES) == {}


def test_validation_rules():
    recipe = a_recipe(
        name="",
        prep_time_minutes=-1,
        ingredients=[
            IngredientInput(name="ข้าว", amount=2, unit="ทัพพี"),
            IngredientInput(name="เกลือ", amount=1, unit="ตามชอบ"),
            IngredientInput(name="", amount=None, unit="กรัม"),
            IngredientInput(name="น้ำ", amount=0, unit=""),
        ],
    )
    errors = recipes.validate_recipe(recipe, UNIT_NAMES)
    assert set(errors) == {
        "name",
        "prep_time_minutes",
        "ingredients[0].unit",
        "ingredients[1].amount",
        "ingredients[2].name",
        "ingredients[2].amount",
        "ingredients[3].unit",
        "ingredients[3].amount",
    }
    assert "ทัพพี" in errors["ingredients[0].unit"]


def test_no_ingredients_is_an_error():
    assert "ingredients" in recipes.validate_recipe(a_recipe(ingredients=[]), UNIT_NAMES)


def test_parse_form_reads_fractions_and_skips_blank_rows():
    form = FormData(
        [
            ("name", " ไข่เจียว "),
            ("prep_time_minutes", "10"),
            ("ingredient_name", "ไข่ไก่"),
            ("ingredient_amount", "3"),
            ("ingredient_unit", "ฟอง"),
            ("ingredient_name", "น้ำปลา"),
            ("ingredient_amount", "1/2"),
            ("ingredient_unit", "ช้อนชา"),
            ("ingredient_name", ""),
            ("ingredient_amount", ""),
            ("ingredient_unit", ""),
        ]
    )
    recipe, errors = recipes.parse_form(form)
    assert errors == {}
    assert recipe.name == "ไข่เจียว"
    assert recipe.prep_time_minutes == 10
    assert [(i.name, i.amount, i.unit) for i in recipe.ingredients] == [
        ("ไข่ไก่", 3.0, "ฟอง"),
        ("น้ำปลา", 0.5, "ช้อนชา"),
    ]


def test_parse_form_reports_bad_numbers():
    form = FormData(
        [
            ("name", "x"),
            ("prep_time_minutes", "ten"),
            ("ingredient_name", "ไข่"),
            ("ingredient_amount", "two"),
            ("ingredient_unit", "ฟอง"),
        ]
    )
    _, errors = recipes.parse_form(form)
    assert set(errors) == {"prep_time_minutes", "ingredients[0].amount"}
