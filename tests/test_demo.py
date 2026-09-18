import asyncio
import time

import pytest

from app.demo import DemoProvider, DemoSwitches
from app.provider import ProviderServerError
from tests.fakes import FakeProvider, make_draft


async def test_no_switches_passes_through():
    draft = make_draft()
    provider = DemoProvider(FakeProvider(draft), DemoSwitches())
    assert await provider.extract("text") == draft


async def test_error_switch_raises_server_error_without_calling_the_model():
    inner = FakeProvider(make_draft())
    provider = DemoProvider(inner, DemoSwitches(error=True))
    with pytest.raises(ProviderServerError):
        await provider.extract("text")
    assert inner.calls == 0


async def test_slow_switch_delays_then_answers():
    provider = DemoProvider(FakeProvider(make_draft()), DemoSwitches(slow=True), slow_seconds=0.1)
    started = time.monotonic()
    await provider.extract("text")
    assert time.monotonic() - started >= 0.1


async def test_hang_switch_never_answers():
    provider = DemoProvider(FakeProvider(make_draft()), DemoSwitches(hang=True))
    with pytest.raises(TimeoutError):
        await asyncio.wait_for(provider.extract("text"), 0.05)


async def test_switches_are_read_on_every_call():
    switches = DemoSwitches()
    provider = DemoProvider(FakeProvider(make_draft()), switches)
    await provider.extract("text")
    switches.error = True
    with pytest.raises(ProviderServerError):
        await provider.extract("text")
