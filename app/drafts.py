"""What an Extraction can produce: a Draft, a Rejected Draft, or a Fallback."""

from dataclasses import dataclass

from pydantic import BaseModel, Field


class DraftIngredient(BaseModel):
    name: str = Field(description="Name of the ingredient, as written in the text.")
    amount: float | None = Field(
        description="How much, as a decimal number (1/2 is 0.5). Null only for ตามชอบ."
    )
    unit: str = Field(description="One Unit from the allowed list, written in Thai.")


class Draft(BaseModel):
    """The model's structured suggestion. The same text can give a different Draft each time."""

    recipe_name: str = Field(description="Name of the dish.")
    ingredients: list[DraftIngredient] = Field(description="Every ingredient in the text.")
    prep_time_minutes: int | None = Field(
        description="Prep time in minutes, or null if the text does not say."
    )


@dataclass(frozen=True)
class Problem:
    """One broken rule in a Draft. `field` is a path such as `ingredients[2].unit`."""

    field: str
    message: str


@dataclass(frozen=True)
class RejectedDraft:
    """A Draft that breaks recipe rules. It still goes to Review, with its problems marked."""

    draft: Draft
    problems: list[Problem]


@dataclass(frozen=True)
class Fallback:
    """No Draft at all. The person gets an empty form, their Recipe Text, and the reason."""

    recipe_text: str
    reason: str


class ExtractionFailed(Exception):
    """The model gave nothing usable. `reason` is written for the person, not the developer."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason
