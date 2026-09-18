"""Calls the real Gemini API. Skipped unless run with `uv run pytest -m live` and a key."""

import pytest

from app.config import load_settings
from app.drafts import Draft
from app.provider import GeminiProvider
from app.routes.extract import read_sample

pytestmark = pytest.mark.live


async def test_sample_01_gives_a_draft():
    settings = load_settings()
    if not settings.gemini_api_key:
        pytest.skip("GEMINI_API_KEY is not set")
    provider = GeminiProvider(settings.gemini_api_key, settings.gemini_model)
    draft = await provider.extract(read_sample("01-nam-prik-kapi"))
    assert isinstance(draft, Draft)
    assert draft.ingredients
