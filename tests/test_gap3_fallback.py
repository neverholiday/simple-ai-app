"""Gap 3: extract_or_fallback. Run with `uv run pytest tests/test_gap3_fallback.py`."""

from app.drafts import Draft, DraftIngredient, Fallback, RejectedDraft
from app.provider import ProviderClientError, ProviderServerError
from app.units import UNIT_NAMES
from tests.fakes import HANG, FakeProvider, make_draft

FAST = {"timeout": 0.05, "attempts": 2, "backoff": 0.01}
TEXT = "น้ำพริกกะปิ กะปิ 1 ช้อนโต๊ะ"


async def test_draft_passes_through(gaps):
    result = await gaps.extract_or_fallback(TEXT, FakeProvider(make_draft()), UNIT_NAMES, **FAST)
    assert isinstance(result, Draft)


async def test_rejected_draft_passes_through(gaps):
    bad = make_draft(ingredients=[DraftIngredient(name="น้ำปลา", amount=1, unit="ทัพพี")])
    result = await gaps.extract_or_fallback(TEXT, FakeProvider(bad), UNIT_NAMES, **FAST)
    assert isinstance(result, RejectedDraft)


async def test_timeout_becomes_fallback_that_keeps_the_text(gaps):
    result = await gaps.extract_or_fallback(TEXT, FakeProvider(HANG), UNIT_NAMES, **FAST)
    assert isinstance(result, Fallback)
    assert result.recipe_text == TEXT
    assert result.reason


async def test_server_error_becomes_fallback(gaps):
    provider = FakeProvider(ProviderServerError("boom"))
    result = await gaps.extract_or_fallback(TEXT, provider, UNIT_NAMES, **FAST)
    assert isinstance(result, Fallback)
    assert provider.calls == 2, "Gap 3 should use Gap 2, including its retry"


async def test_client_error_becomes_fallback_with_its_reason(gaps):
    provider = FakeProvider(ProviderClientError("The model refused the request (403)."))
    result = await gaps.extract_or_fallback(TEXT, provider, UNIT_NAMES, **FAST)
    assert isinstance(result, Fallback)
    assert "403" in result.reason
