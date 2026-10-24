"""
ScamGraph AI - Safety & Response Assistant API Router
Provides interactive risk assessment checklists, immediate incident response plans,
and verified Indian cybercrime reporting resources.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.schemas.safety import SafetyAssessmentRequest, SafetyResponseData
from app.services.safety_service import safety_service

router = APIRouter(prefix="/safety", tags=["Safety & Response"])


@router.post("/assess", response_model=SafetyResponseData)
def assess_victim_situation(payload: SafetyAssessmentRequest):
    """
    Evaluates victim compromise state and generates prioritized emergency actions,
    contact numbers, and official portals.
    """
    plan = safety_service.generate_recommendations(
        has_paid=payload.has_paid,
        shared_otp=payload.shared_otp,
        shared_id=payload.shared_id,
        clicked_link=payload.clicked_link,
        amount_lost=payload.amount_lost,
        payment_reference=payload.payment_reference,
    )
    return plan


@router.get("/portals")
def get_official_portals():
    """Returns verified Indian cybercrime and financial fraud reporting portals."""
    return {
        "portals": safety_service.OFFICIAL_PORTALS,
        "disclaimer": safety_service.DISCLAIMER,
    }
