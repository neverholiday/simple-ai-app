"""Demo Switches: force a model behaviour on demand, the same way every time."""

import asyncio
from dataclasses import dataclass

from app.drafts import Draft
from app.provider import Provider, ProviderServerError

SLOW_SECONDS = 8.0
DEFAULT_TIMEOUT = 20.0
# Not in the Unit list, so a Draft carrying it is always rejected.
INVENTED_UNIT = "ทัพพี"


@dataclass
class DemoSwitches:
    slow: bool = False
    hang: bool = False
    error: bool = False
    bad_unit: bool = False
    # Shortening this makes the Hang demo end sooner; 20s is above a normal answer.
    timeout: float = DEFAULT_TIMEOUT

    def active(self) -> list[str]:
        names = {"slow": "Slow", "hang": "Hang", "error": "Error", "bad_unit": "Bad Unit"}
        return [label for name, label in names.items() if getattr(self, name)]


class DemoProvider:
    """Wraps the real Provider. Switches are read on every call, so they change live."""

    def __init__(self, inner: Provider, switches: DemoSwitches, slow_seconds: float = SLOW_SECONDS):
        self.inner = inner
        self.switches = switches
        self.slow_seconds = slow_seconds

    async def extract(self, recipe_text: str) -> Draft:
        if self.switches.error:
            raise ProviderServerError("The model service failed (Demo Switch: Error).")
        if self.switches.hang:
            await asyncio.Event().wait()  # never set: the call never answers
        if self.switches.slow:
            await asyncio.sleep(self.slow_seconds)
        draft = await self.inner.extract(recipe_text)
        if self.switches.bad_unit and draft.ingredients:
            # The model answered; its first Unit is replaced with one that cannot be saved.
            draft = draft.model_copy(deep=True)
            draft.ingredients[0].unit = INVENTED_UNIT
        return draft
