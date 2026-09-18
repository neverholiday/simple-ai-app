"""Settings read from the environment or a `.env` file."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_MODEL = "gemini-3.1-flash-lite"


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None
    gemini_model: str
    db_path: Path


def load_settings() -> Settings:
    load_dotenv(override=False)
    return Settings(
        gemini_api_key=os.environ.get("GEMINI_API_KEY") or None,
        gemini_model=os.environ.get("GEMINI_MODEL") or DEFAULT_MODEL,
        db_path=Path(os.environ.get("RECIPES_DB") or "recipes.db"),
    )
