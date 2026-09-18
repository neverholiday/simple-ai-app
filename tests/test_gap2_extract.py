"""Gap 2: extract with timeout and retry. Run with `uv run pytest tests/test_gap2_extract.py`.

Timeouts here are much shorter than in the app so the tests run fast.
"""

import time

import pytest

from app.drafts import Draft, DraftIngredient, ExtractionFailed, RejectedDraft
from app.provider import (
    ProviderBadOutput,
    ProviderClientError,
    ProviderNotConfigured,
    ProviderServerError,
)
from app.units import UNIT_NAMES
from tests.fakes import HANG, FakeProvider, make_draft

FAST = {"timeout": 0.05, "attempts": 2, "backoff": 0.01}


async def test_returns_a_valid_draft(gaps):
    draft = make_draft()
    provider = FakeProvider(draft)
    result = await gaps.extract("text", provider, UNIT_NAMES, **FAST)
    assert isinstance(result, Draft)
    assert result == draft
    assert provider.calls == 1


async def test_server_error_is_retried_then_succeeds(gaps):
    provider = FakeProvider(ProviderServerError("boom"), make_draft())
    result = await gaps.extract("text", provider, UNIT_NAMES, **FAST)
    assert isinstance(result, Draft)
    assert provider.calls == 2


async def test_timeout_is_retried_then_succeeds(gaps):
    provider = FakeProvider(HANG, make_draft())
    result = await gaps.extract("text", provider, UNIT_NAMES, **FAST)
    assert isinstance(result, Draft)
    assert provider.calls == 2


async def test_gives_up_after_all_attempts_time_out(gaps):
    provider = FakeProvider(HANG)
    started = time.monotonic()
    with pytest.raises(ExtractionFailed) as failed:
        await gaps.extract("text", provider, UNIT_NAMES, **FAST)
    assert provider.calls == 2
    assert failed.value.reason, "ExtractionFailed needs a reason a person can read"
    # Each attempt must be cut off by the timeout, not wait forever.
    assert time.monotonic() - started < 1


async def test_gives_up_after_all_attempts_fail(gaps):
    provider = FakeProvider(ProviderServerError("boom"))
    with pytest.raises(ExtractionFailed):
        await gaps.extract("text", provider, UNIT_NAMES, **FAST)
    assert provider.calls == 2


@pytest.mark.parametrize(
    "error",
    [
        ProviderClientError("bad key"),
        ProviderBadOutput("not JSON"),
        ProviderNotConfigured("no key"),
    ],
)
async def test_errors_that_retrying_cannot_fix_are_not_retried(gaps, error):
    provider = FakeProvider(error, make_draft())
    with pytest.raises(ExtractionFailed):
        await gaps.extract("text", provider, UNIT_NAMES, **FAST)
    assert provider.calls == 1


async def test_rejected_draft_is_returned_and_never_retried(gaps):
    bad = make_draft(ingredients=[DraftIngredient(name="น้ำปลา", amount=1, unit="ทัพพี")])
    provider = FakeProvider(bad, make_draft())
    result = await gaps.extract("text", provider, UNIT_NAMES, **FAST)
    assert isinstance(result, RejectedDraft)
    assert result.draft == bad
    assert [p.field for p in result.problems] == ["ingredients[0].unit"]
    assert provider.calls == 1


async def test_uses_the_attempts_setting(gaps):
    provider = FakeProvider(ProviderServerError("boom"))
    with pytest.raises(ExtractionFailed):
        await gaps.extract("text", provider, UNIT_NAMES, timeout=0.05, attempts=3, backoff=0.01)
    assert provider.calls == 3
