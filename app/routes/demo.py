"""The Demo Switches page. Changes apply to the next Extraction, with no restart."""

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.demo import SLOW_SECONDS
from app.routes.common import render

router = APIRouter()


@router.get("/demo")
def demo_page(request: Request):
    return render(
        request,
        "demo.html",
        {
            "key_configured": request.app.state.settings.gemini_api_key is not None,
            "model": request.app.state.settings.gemini_model,
            "slow_seconds": SLOW_SECONDS,
        },
    )


@router.post("/demo")
async def update_switches(request: Request):
    form = await request.form()
    switches = request.app.state.switches
    switches.slow = "slow" in form
    switches.hang = "hang" in form
    switches.error = "error" in form
    return RedirectResponse("/demo", status_code=303)
