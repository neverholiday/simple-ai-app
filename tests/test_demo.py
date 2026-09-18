import asyncio
import time

import pytest

from app.demo import INVENTED_UNIT, DemoProvider, DemoSwitches
from app.provider import ProviderServerError
from app.units import UNIT_NAMES
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


async def test_bad_unit_switch_replaces_the_first_unit():
    provider = DemoProvider(FakeProvider(make_draft()), DemoSwitches(bad_unit=True))
    draft = await provider.extract("text")
    assert draft.ingredients[0].unit == INVENTED_UNIT
    assert draft.ingredients[0].unit not in UNIT_NAMES
    assert draft.ingredients[1].unit == "เม็ด", "only the first Unit changes"


async def test_bad_unit_switch_leaves_the_original_draft_alone():
    original = make_draft()
    provider = DemoProvider(FakeProvider(original), DemoSwitches(bad_unit=True))
    await provider.extract("text")
    assert original.ingredients[0].unit == "ช้อนโต๊ะ"


def test_active_lists_readable_names():
    assert DemoSwitches(slow=True, bad_unit=True).active() == ["Slow", "Bad Unit"]
    assert DemoSwitches().active() == []
