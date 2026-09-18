"""Extraction: paste Recipe Text, get a Draft, a Rejected Draft or a Fallback, then Review."""

from pathlib import Path

from fastapi import APIRouter, Request

from app.drafts import Draft, Fallback, RejectedDraft
from app.routes.common import form_values, render
from app.units import UNIT_NAMES

router = APIRouter()

SAMPLES_DIR = Path(__file__).resolve().parents[2] / "samples"


def list_samples() -> list[str]:
    return sorted(path.stem for path in SAMPLES_DIR.glob("*.txt"))


def read_sample(name: str) -> str:
    if name not in list_samples():
        return ""
    # Always UTF-8: on Windows the default encoding would garble Thai text.
    return (SAMPLES_DIR / f"{name}.txt").read_text(encoding="utf-8")


@router.get("/extract")
def extract_page(request: Request, sample: str = ""):
    return render(
        request,
        "extract.html",
        {"samples": list_samples(), "selected": sample, "recipe_text": read_sample(sample)},
    )


@router.post("/extract")
async def run_extraction(request: Request):
    form = await request.form()
    recipe_text = (form.get("recipe_text") or "").strip()
    if not recipe_text:
        return render(
            request,
            "extract.html",
            {"samples": list_samples(), "selected": "", "recipe_text": "", "empty": True},
            status_code=422,
        )

    gaps = request.app.state.gaps
    try:
        result = await gaps.extract_or_fallback(
            recipe_text,
            request.app.state.provider,
            UNIT_NAMES,
            timeout=request.app.state.switches.timeout,
        )
    except NotImplementedError as exc:
        return render(request, "gap_missing.html", {"message": str(exc)}, status_code=501)

    context = {"title": "Review the Draft", "action": "/recipes", "recipe_text": recipe_text}
    if isinstance(result, Fallback):
        context.update(
            title="Fill in the recipe by hand",
            mode="fallback",
            values=form_values(None),
            errors={},
            reason=result.reason,
        )
    elif isinstance(result, RejectedDraft):
        errors = {
            problem.field.replace("recipe_name", "name"): problem.message
            for problem in result.problems
        }
        context.update(mode="rejected", values=form_values(result.draft), errors=errors)
    elif isinstance(result, Draft):
        context.update(mode="review", values=form_values(result), errors={})
    else:
        raise TypeError(f"extract_or_fallback returned {type(result).__name__}")
    # Nothing is saved here. The Draft only fills the form; Review decides.
    return render(request, "recipe_form.html", context)
