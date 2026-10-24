"""
ScamGraph AI - Dashboard Analytics API Router
Provides real-time metrics, risk severity breakdowns, indicator distributions,
and threat intelligence activity timelines for the futuristic cyber dashboard.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database.session import get_db
from app.models.investigation import (
    Investigation,
    InvestigationStatus,
    Entity,
    Indicator,
    Relationship,
    EvidenceSource,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Computes high-level intelligence metrics for the main overview dashboard."""
    total_investigations = db.query(Investigation).count()
    confirmed_scams = db.query(Investigation).filter(Investigation.status == InvestigationStatus.CONFIRMED_SCAM.value).count()
    suspicious_cases = db.query(Investigation).filter(Investigation.status == InvestigationStatus.SUSPICIOUS.value).count()
    benign_cases = db.query(Investigation).filter(Investigation.status == InvestigationStatus.BENIGN.value).count()
    
    total_entities = db.query(Entity).count()
    total_indicators = db.query(Indicator).count()
    total_relationships = db.query(Relationship).count()
    total_evidence_sources = db.query(EvidenceSource).count()

    # Average risk score
    avg_risk = db.query(func.avg(Investigation.overall_risk_score)).scalar() or 0.0

    # Indicator breakdown by category
    indicator_counts = (
        db.query(Indicator.indicator_category, func.count(Indicator.id))
        .group_by(Indicator.indicator_category)
        .order_by(func.count(Indicator.id).desc())
        .limit(6)
        .all()
    )
    category_distribution = [{"category": cat, "count": cnt} for cat, cnt in indicator_counts]

    # Entity types breakdown
    entity_counts = (
        db.query(Entity.entity_type, func.count(Entity.id))
        .group_by(Entity.entity_type)
        .order_by(func.count(Entity.id).desc())
        .all()
    )
    entity_distribution = [{"type": etype, "count": cnt} for etype, cnt in entity_counts]

    # Top high risk entities
    high_risk_entities = (
        db.query(Entity)
        .filter(Entity.risk_score >= 80.0)
        .order_by(Entity.risk_score.desc())
        .limit(8)
        .all()
    )
    top_threats = [
        {
            "id": e.id,
            "type": e.entity_type,
            "label": e.display_label,
            "value": e.normalized_value,
            "risk_score": e.risk_score,
            "investigation_id": e.investigation_id,
        }
        for e in high_risk_entities
    ]

    # Recent activity cases
    recent_cases = (
        db.query(Investigation)
        .order_by(Investigation.created_at.desc())
        .limit(5)
        .all()
    )
    recent_activity = [
        {
            "id": inv.id,
            "case_number": inv.case_number,
            "title": inv.title,
            "status": inv.status,
            "risk_score": inv.overall_risk_score,
            "confidence": inv.confidence_level,
            "created_at": inv.created_at,
        }
        for inv in recent_cases
    ]

    return {
        "metrics": {
            "total_investigations": total_investigations,
            "confirmed_scams": confirmed_scams,
            "suspicious_cases": suspicious_cases,
            "benign_cases": benign_cases,
            "total_entities": total_entities,
            "total_indicators": total_indicators,
            "total_relationships": total_relationships,
            "total_evidence_sources": total_evidence_sources,
            "average_risk_score": round(float(avg_risk), 1),
        },
        "category_distribution": category_distribution,
        "entity_distribution": entity_distribution,
        "top_threats": top_threats,
        "recent_activity": recent_activity,
    }
