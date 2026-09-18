"""Choose which version of the Gaps the app uses: the Starter or the Solution."""

import importlib
from types import ModuleType

CHOICES = ("starter", "solution")


def load_gaps(name: str) -> ModuleType:
    if name not in CHOICES:
        raise ValueError(f"Unknown Gaps version {name!r}; use one of {', '.join(CHOICES)}.")
    return importlib.import_module(f"{name}.extraction")
