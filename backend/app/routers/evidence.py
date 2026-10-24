"""
ScamGraph AI - Evidence Explorer API Router
Provides deep provenance exploration across evidence artifacts, extracted indicators,
and TinyFish intelligence records.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.database.session import get_db
from app.models.investigation import (
    EvidenceSource,
    Indicator,
    Investigation,
    Entity,
)

router = APIRouter(prefix="/evidence", tags=["Evidence Explorer"])


@router.get("")
def list_evidence_artifacts(
    source_type: Optional[str] = Query(None),
    investigation_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Lists preserved external and internal evidence records with full provenance."""
    q = db.query(EvidenceSource, Investigation).join(
        Investigation, EvidenceSource.investigation_id == Investigation.id
    )

    if source_type:
        q = q.filter(EvidenceSource.source_type == source_type)
    if investigation_id:
        q = q.filter(EvidenceSource.investigation_id == investigation_id)

    records = q.order_by(EvidenceSource.retrieval_timestamp.desc()).limit(limit).all()

    results = []
    for ev, inv in records:
        results.append({
            "id": ev.id,
            "investigation_id": inv.id,
            "case_number": inv.case_number,
            "investigation_title": inv.title,
            "source_type": ev.source_type,
            "source_url": ev.source_url,
            "page_title": ev.page_title,
            "retrieval_timestamp": ev.retrieval_timestamp,
            "raw_content_preview": ev.raw_content_preview,
            "claims_supported": ev.claims_supported,
            "is_verified": ev.is_verified,
        })
    return results


@router.get("/indicators")
def list_indicators(
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    investigation_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Lists extracted red-flag indicators across investigations with matched quotes."""
    q = db.query(Indicator, Investigation).join(
        Investigation, Indicator.investigation_id == Investigation.id
    )

    if severity:
        q = q.filter(Indicator.severity == severity.upper())
    if category:
        q = q.filter(Indicator.indicator_category == category)
    if investigation_id:
        q = q.filter(Indicator.investigation_id == investigation_id)

    records = q.order_by(Indicator.created_at.desc()).limit(limit).all()

    results = []
    for ind, inv in records:
        results.append({
            "id": ind.id,
            "investigation_id": inv.id,
            "case_number": inv.case_number,
            "investigation_title": inv.title,
            "category": ind.indicator_category,
            "title": ind.title,
            "severity": ind.severity,
            "matched_snippet": ind.matched_snippet,
            "explanation": ind.explanation,
            "weight": ind.weight,
            "created_at": ind.created_at,
        })
    return results
