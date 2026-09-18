"""Demo Switches: force a model behaviour on demand, the same way every time."""

import asyncio
from dataclasses import dataclass

from app.drafts import Draft
from app.provider import Provider, ProviderServerError

SLOW_SECONDS = 4.0


@dataclass
class DemoSwitches:
    slow: bool = False
    hang: bool = False
    error: bool = False

    def active(self) -> list[str]:
        return [name for name in ("slow", "hang", "error") if getattr(self, name)]


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
        return await self.inner.extract(recipe_text)
