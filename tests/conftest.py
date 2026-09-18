from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.demo import DemoSwitches
from app.gaps import load_gaps
from app.main import create_app


@pytest.fixture(scope="session")
def gaps(request):
    """The Gaps under test. Only the tests/test_gap*.py files use this."""
    return load_gaps(request.config.getoption("--use"))


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(gemini_api_key=None, gemini_model="test-model", db_path=tmp_path / "test.db")


@pytest.fixture
def make_client(settings):
    """Build a TestClient around the app. App tests always use the Solution Gaps,
    so they pass whether or not the Starter is finished."""

    def build(provider=None, switches=None):
        app = create_app(
            load_gaps("solution"),
            settings=settings,
            provider=provider,
            switches=switches or DemoSwitches(),
        )
        return TestClient(app)

    return build
