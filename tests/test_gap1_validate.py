"""Gap 1: validate_draft. Run with `uv run pytest tests/test_gap1_validate.py`."""

from app.drafts import DraftIngredient
from app.units import UNIT_NAMES
from tests.fakes import make_draft


def fields(problems):
    return {problem.field for problem in problems}


def test_valid_draft_has_no_problems(gaps):
    assert gaps.validate_draft(make_draft(), UNIT_NAMES) == []


def test_unknown_unit_is_a_problem_that_names_the_unit(gaps):
    draft = make_draft(ingredients=[DraftIngredient(name="น้ำปลา", amount=1, unit="ทัพพี")])
    problems = gaps.validate_draft(draft, UNIT_NAMES)
    assert fields(problems) == {"ingredients[0].unit"}
    assert "ทัพพี" in problems[0].message


def test_to_taste_without_amount_is_valid(gaps):
    draft = make_draft(ingredients=[DraftIngredient(name="เกลือ", amount=None, unit="ตามชอบ")])
    assert gaps.validate_draft(draft, UNIT_NAMES) == []


def test_to_taste_with_amount_is_a_problem(gaps):
    draft = make_draft(ingredients=[DraftIngredient(name="เกลือ", amount=1, unit="ตามชอบ")])
    assert fields(gaps.validate_draft(draft, UNIT_NAMES)) == {"ingredients[0].amount"}


def test_missing_amount_is_a_problem_for_other_units(gaps):
    draft = make_draft(ingredients=[DraftIngredient(name="กะปิ", amount=None, unit="ช้อนโต๊ะ")])
    assert fields(gaps.validate_draft(draft, UNIT_NAMES)) == {"ingredients[0].amount"}


def test_zero_or_negative_amount_is_a_problem(gaps):
    draft = make_draft(
        ingredients=[
            DraftIngredient(name="กะปิ", amount=0, unit="ช้อนโต๊ะ"),
            DraftIngredient(name="กุ้งแห้ง", amount=-2, unit="กรัม"),
        ]
    )
    problems = fields(gaps.validate_draft(draft, UNIT_NAMES))
    assert problems == {"ingredients[0].amount", "ingredients[1].amount"}


def test_empty_name_negative_prep_time_and_no_ingredients(gaps):
    draft = make_draft(recipe_name="  ", prep_time_minutes=-5, ingredients=[])
    problems = fields(gaps.validate_draft(draft, UNIT_NAMES))
    assert problems == {"recipe_name", "prep_time_minutes", "ingredients"}


def test_every_problem_is_listed_not_just_the_first(gaps):
    draft = make_draft(
        ingredients=[
            DraftIngredient(name="", amount=1, unit="ช้อนโต๊ะ"),
            DraftIngredient(name="พริก", amount=None, unit="กำมือ"),
        ]
    )
    problems = fields(gaps.validate_draft(draft, UNIT_NAMES))
    assert problems == {"ingredients[0].name", "ingredients[1].unit", "ingredients[1].amount"}
