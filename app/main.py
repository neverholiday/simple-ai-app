"""Builds the web app."""

from pathlib import Path
from types import ModuleType

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import db
from app.config import Settings, load_settings
from app.demo import DemoProvider, DemoSwitches
from app.provider import GeminiProvider, Provider
from app.routes import demo, extract, recipes
from app.units import TO_TASTE, UNITS

APP_DIR = Path(__file__).parent


def create_app(
    gaps: ModuleType,
    *,
    settings: Settings | None = None,
    provider: Provider | None = None,
    switches: DemoSwitches | None = None,
) -> FastAPI:
    settings = settings or load_settings()
    switches = switches or DemoSwitches()
    real_provider = provider or GeminiProvider(settings.gemini_api_key, settings.gemini_model)

    conn = db.connect(settings.db_path)
    try:
        db.init_db(conn)
    finally:
        conn.close()

    templates = Jinja2Templates(directory=APP_DIR / "templates")
    templates.env.globals.update(
        switches=switches,
        gaps_name=gaps.__name__.split(".")[0],
        units=UNITS,
        to_taste=TO_TASTE,
    )

    app = FastAPI(title="Simple AI App")
    app.state.settings = settings
    app.state.gaps = gaps
    app.state.switches = switches
    # Demo Switches wrap whichever Provider is used, so failures can be forced on demand.
    app.state.provider = DemoProvider(real_provider, switches)
    app.state.templates = templates

    app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
    app.include_router(recipes.router)
    app.include_router(extract.router)
    app.include_router(demo.router)

    @app.get("/", include_in_schema=False)
    def home():
        return RedirectResponse("/recipes", status_code=303)

    return app
