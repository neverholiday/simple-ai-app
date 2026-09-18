"""The Provider: the one doorway through which every Extraction reaches the model."""

from typing import Protocol

import httpx
from google import genai
from google.genai import types
from pydantic import ValidationError

from app.drafts import Draft
from app.units import TO_TASTE, UNITS


class ProviderError(Exception):
    """Base class for everything that can go wrong when calling the model."""


class ProviderServerError(ProviderError):
    """The model service failed or could not be reached. Trying again may work."""


class ProviderClientError(ProviderError):
    """The request was refused, for example a bad key or a rate limit. Retrying will not help."""


class ProviderBadOutput(ProviderError):
    """The model answered, but not with JSON that matches the Draft schema."""


class ProviderNotConfigured(ProviderError):
    """No API key is configured."""


class Provider(Protocol):
    async def extract(self, recipe_text: str) -> Draft: ...


def build_prompt(recipe_text: str) -> str:
    unit_lines = "\n".join(f"- {name} ({label})" for name, label in UNITS)
    return f"""Turn the recipe text below into a recipe.

Use only information in the text.
Write every unit as one of these allowed units, using the Thai name:
{unit_lines}

Map abbreviations to the allowed unit, for example "tbsp" or "ช.ต." to ช้อนโต๊ะ.
Use {TO_TASTE} for "to taste", "a pinch" or "เล็กน้อย", and leave its amount null.
Write amounts as decimal numbers, for example 1/2 as 0.5.

Recipe text:
{recipe_text}
"""


class GeminiProvider:
    def __init__(self, api_key: str | None, model: str):
        self.model = model
        self._client: genai.Client | None = None
        if api_key:
            # The SDK retries failed calls by itself, which would hide the retry students
            # write in Gap 2. The interactions API cannot be set to zero retries (attempts=0
            # becomes 1), so its retries are limited to status 418, which Gemini does not send.
            no_retries = types.HttpRetryOptions(attempts=1, http_status_codes=[418])
            self._client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(retry_options=no_retries),
            )

    async def extract(self, recipe_text: str) -> Draft:
        if self._client is None:
            raise ProviderNotConfigured("No GEMINI_API_KEY is configured.")
        try:
            interaction = await self._client.aio.interactions.create(
                model=self.model,
                input=build_prompt(recipe_text),
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": Draft.model_json_schema(),
                },
            )
        except httpx.HTTPError as exc:
            raise ProviderServerError(f"Could not reach the model: {exc}") from exc
        except Exception as exc:
            status = getattr(exc, "status_code", None)
            if status is None:
                raise
            if status >= 500:
                raise ProviderServerError(f"The model service failed ({status}).") from exc
            raise ProviderClientError(f"The model refused the request ({status}).") from exc

        output = interaction.output_text
        if not output:
            raise ProviderBadOutput("The model returned no text.")
        try:
            return Draft.model_validate_json(output)
        except ValidationError as exc:
            raise ProviderBadOutput("The model returned JSON that does not match a Draft.") from exc
