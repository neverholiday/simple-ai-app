"""A scripted Provider for tests. It never touches the network."""

import asyncio

from app.drafts import Draft, DraftIngredient

HANG = object()


class FakeProvider:
    """Plays back outcomes in order: a Draft to return, an exception to raise, or HANG.

    The last outcome repeats once the others are used up.
    """

    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    async def extract(self, recipe_text: str) -> Draft:
        self.calls += 1
        outcome = self.outcomes.pop(0) if len(self.outcomes) > 1 else self.outcomes[0]
        if outcome is HANG:
            await asyncio.Event().wait()
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def make_draft(**overrides) -> Draft:
    values = {
        "recipe_name": "น้ำพริกกะปิ",
        "prep_time_minutes": 15,
        "ingredients": [
            DraftIngredient(name="กะปิ", amount=1, unit="ช้อนโต๊ะ"),
            DraftIngredient(name="พริกขี้หนู", amount=10, unit="เม็ด"),
            DraftIngredient(name="น้ำตาลปี๊บ", amount=None, unit="ตามชอบ"),
        ],
    }
    values.update(overrides)
    return Draft(**values)
