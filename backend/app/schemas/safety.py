"""
ScamGraph AI - Pydantic Schemas for Safety Guidance and Configuration Settings
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SafetyAssessmentRequest(BaseModel):
    has_paid: bool = False
    shared_otp: bool = False
    shared_id: bool = False
    clicked_link: bool = False
    amount_lost: Optional[float] = None
    payment_reference: Optional[str] = None


class ActionItem(BaseModel):
    priority: str
    title: str
    description: str
    portal_name: Optional[str] = None
    portal_url: Optional[str] = None
    helpline: Optional[str] = None


class OfficialPortal(BaseModel):
    name: str
    url: str
    helpline: Optional[str] = None
    jurisdiction: str
    description: str
    type: str


class SafetyResponseData(BaseModel):
    compromise_summary: Dict[str, Any]
    actions: List[ActionItem]
    official_portals: List[OfficialPortal]
    disclaimer: str


class SettingsUpdateRequest(BaseModel):
    tinyfish_api_key: Optional[str] = None
    tinyfish_base_url: Optional[str] = None
    tinyfish_enabled: Optional[bool] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ai_model_name: Optional[str] = None


class SettingsResponse(BaseModel):
    tinyfish_enabled: bool
    tinyfish_configured: bool
    tinyfish_base_url: str
    ai_model_name: str
    openai_configured: bool
    gemini_configured: bool
    anthropic_configured: bool
