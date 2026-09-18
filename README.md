# Simple AI App

A recipe app that turns messy Recipe Text into a Draft with Gemini. A Draft is only a suggestion: nothing is saved until you review it.

**You need:** a Gemini API key from https://aistudio.google.com/apikey, and `uv`:

```sh
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Setup:** copy `.env.example` to `.env` (`cp` on macOS, `copy` on Windows) and paste your key after `GEMINI_API_KEY=`. Then:

```sh
uv sync
```

That one command installs the right Python and every package the app needs, including `google-genai`, into `.venv`. There is no `pip install` step: `uv run` always uses that environment.

**Run the finished app** (hands-on 1):

```sh
uv run python -m app --use solution
```

Open http://127.0.0.1:8000. Try the Samples on "Extract from text" and the switches on "Demo Switches".

**Write the Gaps** (hands-on 2): the three functions in `starter/extraction.py`. Do them in order and check each one:

```sh
uv run pytest tests/test_gap1_validate.py
uv run pytest tests/test_gap2_extract.py
uv run pytest tests/test_gap3_fallback.py
uv run python -m app --use starter
```

Stuck? `solution/extraction.py` has the answers.

**All tests:** `uv run pytest --use solution`. `uv run pytest -m live` calls the real Gemini API.
