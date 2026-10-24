"""
ScamGraph AI - Settings and API Configuration Router
Manages external research service toggles, API keys, and system diagnostics safely.
"""

from fastapi import APIRouter
from app.config import settings
from app.schemas.safety import SettingsUpdateRequest, SettingsResponse
from app.services.tinyfish_service import tinyfish_service

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=SettingsResponse)
def get_current_settings():
    """Returns safe masked system settings without exposing private keys."""
    return SettingsResponse(
        tinyfish_enabled=settings.TINYFISH_ENABLED,
        tinyfish_configured=bool(settings.TINYFISH_API_KEY),
        tinyfish_base_url=settings.TINYFISH_API_BASE_URL,
        ai_model_name=settings.AI_MODEL_NAME,
        openai_configured=bool(settings.OPENAI_API_KEY),
        gemini_configured=bool(settings.GEMINI_API_KEY),
        anthropic_configured=bool(settings.ANTHROPIC_API_KEY),
    )


@router.post("")
def update_settings(payload: SettingsUpdateRequest):
    """Updates runtime configuration settings."""
    if payload.tinyfish_api_key is not None:
        settings.TINYFISH_API_KEY = payload.tinyfish_api_key
        tinyfish_service.api_key = payload.tinyfish_api_key
    if payload.tinyfish_base_url is not None:
        settings.TINYFISH_API_BASE_URL = payload.tinyfish_base_url
        tinyfish_service.base_url = payload.tinyfish_base_url.rstrip("/")
    if payload.tinyfish_enabled is not None:
        settings.TINYFISH_ENABLED = payload.tinyfish_enabled
        tinyfish_service.is_enabled = payload.tinyfish_enabled and bool(settings.TINYFISH_API_KEY)
    if payload.openai_api_key is not None:
        settings.OPENAI_API_KEY = payload.openai_api_key
    if payload.gemini_api_key is not None:
        settings.GEMINI_API_KEY = payload.gemini_api_key
    if payload.anthropic_api_key is not None:
        settings.ANTHROPIC_API_KEY = payload.anthropic_api_key
    if payload.ai_model_name is not None:
        settings.AI_MODEL_NAME = payload.ai_model_name

    return {
        "status": "success",
        "message": "Settings updated successfully.",
        "tinyfish_status": tinyfish_service.get_status(),
    }


@router.post("/test-tinyfish")
async def test_tinyfish_connection():
    """Tests connection to configured TinyFish API endpoint."""
    status = tinyfish_service.get_status()
    return status
