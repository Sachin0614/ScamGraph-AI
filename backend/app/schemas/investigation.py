"""
ScamGraph AI - Pydantic Schemas for Investigations and Evidence
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class InvestigationCreate(BaseModel):
    title: Optional[str] = None
    raw_text: Optional[str] = Field(None, description="Suspicious job offer or message text")
    website_url: Optional[str] = Field(None, description="Fraudulent website or recruitment portal URL")
    recruiter_name: Optional[str] = Field(None, description="Claimed recruiter or HR contact name")
    email: Optional[str] = Field(None, description="Sender email address")
    phone: Optional[str] = Field(None, description="Contact phone or WhatsApp number")
    payment_id: Optional[str] = Field(None, description="UPI ID, wallet address, or bank account requested")
    notes: Optional[str] = Field(None, description="Additional context or submission notes")


class IndicatorResponse(BaseModel):
    id: Optional[int] = None
    category: str
    title: str
    severity: str
    matched_snippet: Optional[str] = None
    explanation: str
    weight: Optional[float] = 1.0


class EntityResponse(BaseModel):
    id: int
    entity_type: str
    raw_value: str
    normalized_value: str
    display_label: str
    risk_score: float
    has_geocoding: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RelationshipResponse(BaseModel):
    id: int
    source_entity_id: int
    target_entity_id: int
    relationship_type: str
    confidence: float
    matching_indicator: str
    evidence_reason: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvidenceSourceResponse(BaseModel):
    id: int
    source_type: str
    source_url: Optional[str] = None
    page_title: Optional[str] = None
    retrieval_timestamp: datetime
    raw_content_preview: Optional[str] = None
    claims_supported: Optional[str] = None
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class AnalysisResultResponse(BaseModel):
    risk_verdict: str
    overall_risk_score: float
    detected_indicators: List[Dict[str, Any]] = []
    exact_snippets: Dict[str, str] = {}
    missing_inconsistencies: List[str] = []
    recommended_verification_steps: List[str] = []
    confidence_explanation: Optional[str] = None
    limitations_and_uncertainty: Optional[str] = None
    ai_engine_used: str = "rule-engine-v2"


class InvestigationProgressEvent(BaseModel):
    stage: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class InvestigationDetail(BaseModel):
    id: int
    case_number: str
    title: str
    raw_text: Optional[str] = None
    submitter_notes: Optional[str] = None
    status: str
    overall_risk_score: float
    confidence_level: str
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    entities: List[EntityResponse] = []
    indicators: List[IndicatorResponse] = []
    evidence_sources: List[EvidenceSourceResponse] = []
    analysis_results: Optional[AnalysisResultResponse] = None
    events: List[InvestigationProgressEvent] = []

    model_config = ConfigDict(from_attributes=True)


class InvestigationSummary(BaseModel):
    id: int
    case_number: str
    title: str
    status: str
    overall_risk_score: float
    confidence_level: str
    summary: Optional[str] = None
    created_at: datetime
    entities_count: int = 0
    indicators_count: int = 0

    model_config = ConfigDict(from_attributes=True)
