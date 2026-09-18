"""The web flow: a Draft only fills the form; nothing is saved until Review submits it."""

import time

from app import db
from app.drafts import DraftIngredient
from app.gaps import load_gaps
from app.main import create_app
from app.provider import ProviderServerError
from tests.fakes import HANG, FakeProvider, make_draft

TEXT = "น้ำพริกกะปิ กะปิ 1 ช้อนโต๊ะ"


def recipe_count(settings) -> int:
    conn = db.connect(settings.db_path)
    try:
        return conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    finally:
        conn.close()


def form_rows(*rows):
    data = {"name": [], "ingredient_name": [], "ingredient_amount": [], "ingredient_unit": []}
    for name, amount, unit in rows:
        data["ingredient_name"].append(name)
        data["ingredient_amount"].append(amount)
        data["ingredient_unit"].append(unit)
    return data


def test_manual_entry_create_edit_delete(make_client):
    client = make_client()
    data = form_rows(("ไข่ไก่", "3", "ฟอง"), ("น้ำปลา", "1/2", "ช้อนชา"))
    data["name"] = "ไข่เจียว"
    response = client.post("/recipes", data=data, follow_redirects=False)
    assert response.status_code == 303
    location = response.headers["location"]

    page = client.get(location).text
    assert "ไข่เจียว" in page
    assert "0.5" in page

    data["name"] = "ไข่เจียวหมูสับ"
    assert client.post(location, data=data, follow_redirects=False).status_code == 303
    assert "ไข่เจียวหมูสับ" in client.get(location).text

    assert client.post(f"{location}/delete", follow_redirects=False).status_code == 303
    assert client.get(location).status_code == 404


def test_invalid_manual_entry_is_not_saved(make_client, settings):
    client = make_client()
    data = form_rows(("ข้าว", "2", "ทัพพี"))
    data["name"] = "ข้าวผัด"
    response = client.post("/recipes", data=data)
    assert response.status_code == 422
    assert "is not an allowed Unit" in response.text
    assert recipe_count(settings) == 0


def test_draft_fills_the_form_but_saves_nothing(make_client, settings):
    client = make_client(provider=FakeProvider(make_draft()))
    response = client.post("/extract", data={"recipe_text": TEXT})
    assert response.status_code == 200
    assert "Draft from the model" in response.text
    assert 'value="กะปิ"' in response.text
    assert TEXT in response.text, "the Recipe Text stays beside the form"
    assert recipe_count(settings) == 0


def test_review_save_creates_the_recipe(make_client, settings):
    client = make_client(provider=FakeProvider(make_draft()))
    data = form_rows(("กะปิ", "1", "ช้อนโต๊ะ"), ("น้ำตาลปี๊บ", "", "ตามชอบ"))
    data.update(name="น้ำพริกกะปิ", mode="review", recipe_text=TEXT)
    response = client.post("/recipes", data=data, follow_redirects=False)
    assert response.status_code == 303
    assert recipe_count(settings) == 1


def test_rejected_draft_keeps_the_wrong_value_and_marks_it(make_client, settings):
    bad = make_draft(ingredients=[DraftIngredient(name="ข้าวสวย", amount=2, unit="ทัพพี")])
    client = make_client(provider=FakeProvider(bad))
    response = client.post("/extract", data={"recipe_text": TEXT})
    assert "Rejected Draft" in response.text
    assert "ทัพพี (not allowed)" in response.text
    assert "is not an allowed Unit" in response.text
    assert recipe_count(settings) == 0

    # Saving it unchanged is refused, and the person stays in Review with the text.
    data = form_rows(("ข้าวสวย", "2", "ทัพพี"))
    data.update(name="ข้าวผัด", mode="rejected", recipe_text=TEXT)
    response = client.post("/recipes", data=data)
    assert response.status_code == 422
    assert TEXT in response.text
    assert recipe_count(settings) == 0


def test_provider_failure_gives_fallback_with_text_kept(make_client):
    client = make_client(provider=FakeProvider(ProviderServerError("boom")))
    response = client.post("/extract", data={"recipe_text": TEXT})
    assert response.status_code == 200
    assert "Fallback" in response.text
    assert TEXT in response.text


def test_no_api_key_gives_fallback_and_app_still_starts(make_client):
    client = make_client()  # no provider injected: the real Gemini provider, with no key
    response = client.post("/extract", data={"recipe_text": TEXT})
    assert "Fallback" in response.text
    assert "No GEMINI_API_KEY" in response.text


def test_starter_gaps_show_gap_missing_page_and_crud_still_works(settings):
    from fastapi.testclient import TestClient

    client = TestClient(
        create_app(load_gaps("starter"), settings=settings, provider=FakeProvider(make_draft()))
    )
    response = client.post("/extract", data={"recipe_text": TEXT})
    assert response.status_code == 501
    assert "Gap 3" in response.text
    assert client.get("/recipes/new").status_code == 200


def test_demo_switches_page_updates_live(make_client):
    client = make_client(provider=FakeProvider(make_draft()))
    client.post("/demo", data={"error": "on"})
    response = client.post("/extract", data={"recipe_text": TEXT})
    assert "Fallback" in response.text
    assert "Demo Switch: Error" in response.text

    client.post("/demo", data={})
    response = client.post("/extract", data={"recipe_text": TEXT})
    assert "Draft from the model" in response.text


def test_bad_unit_switch_forces_a_rejected_draft(make_client, settings):
    client = make_client(provider=FakeProvider(make_draft()))
    client.post("/demo", data={"bad_unit": "on"})
    response = client.post("/extract", data={"recipe_text": TEXT})
    assert "Rejected Draft" in response.text
    assert "is not an allowed Unit" in response.text
    assert recipe_count(settings) == 0


def test_timeout_from_the_demo_page_is_used(make_client):
    client = make_client(provider=FakeProvider(HANG))
    client.post("/demo", data={"timeout": "0.05"})  # clamped up to the 1s minimum
    started = time.monotonic()
    response = client.post("/extract", data={"recipe_text": TEXT})
    assert "Fallback" in response.text
    assert "1 seconds" in response.text
    assert time.monotonic() - started < 8, "the page timeout must replace the 20s default"


def test_demo_page_rejects_a_silly_timeout(make_client):
    client = make_client()
    client.post("/demo", data={"timeout": "not a number"})
    assert 'value="20"' in client.get("/demo").text


def test_sample_loads_into_the_textarea(make_client):
    client = make_client()
    response = client.get("/extract", params={"sample": "01-nam-prik-kapi"})
    assert "กะปิ 1 ช้อนโต๊ะ" in response.text
