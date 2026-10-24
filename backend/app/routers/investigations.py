"""
ScamGraph AI - Investigation API Router
Implements the 10-stage investigation submission pipeline, case management, and detail exploration.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import uuid

from app.database.session import get_db
from app.models.investigation import (
    Investigation,
    InvestigationStatus,
    Entity,
    EntityType,
    Indicator,
    Relationship,
    RelationshipType,
    EvidenceSource,
    EvidenceSourceType,
    AnalysisResult,
    RecommendedAction,
    InvestigationEvent,
)
from app.schemas.investigation import (
    InvestigationCreate,
    InvestigationDetail,
    InvestigationSummary,
    InvestigationProgressEvent,
    EntityResponse,
    IndicatorResponse,
    EvidenceSourceResponse,
    AnalysisResultResponse,
)
from app.services.normalizer import normalizer, SSRFValidationError
from app.services.scam_engine import scam_engine
from app.services.relationship_engine import relationship_engine
from app.services.tinyfish_service import tinyfish_service
from app.services.safety_service import safety_service

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.get("", response_model=List[InvestigationSummary])
def list_investigations(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Retrieves paginated list of investigations with search and status filters."""
    query = db.query(Investigation)
    if status_filter:
        query = query.filter(Investigation.status == status_filter.upper())
    if search:
        s = f"%{search}%"
        query = query.filter(
            (Investigation.title.ilike(s)) |
            (Investigation.case_number.ilike(s)) |
            (Investigation.raw_text.ilike(s))
        )

    investigations = query.order_by(Investigation.created_at.desc()).offset(offset).limit(limit).all()

    results = []
    for inv in investigations:
        results.append(
            InvestigationSummary(
                id=inv.id,
                case_number=inv.case_number,
                title=inv.title,
                status=inv.status,
                overall_risk_score=inv.overall_risk_score,
                confidence_level=inv.confidence_level,
                summary=inv.summary,
                created_at=inv.created_at,
                entities_count=len(inv.entities),
                indicators_count=len(inv.indicators),
            )
        )
    return results


@router.post("", response_model=InvestigationDetail, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    payload: InvestigationCreate,
    db: Session = Depends(get_db),
):
    """
    Executes the comprehensive 10-stage ScamGraph AI Investigation Pipeline:
    1. Input Validation & Indicator Normalization
    2. Investigation Record Creation
    3. Behavioral Scam Pattern Analysis
    4. Entity Graph Node Generation
    5. External Intelligence via TinyFish
    6. Historical Evidence Correlation
    7. Evidence-backed Relationship Linking
    8. Topological Graph Updates
    9. Actionable Intelligence Report
    10. Tailored Safety Recommendations
    """
    # Verify at least one piece of information was submitted
    if not any([payload.raw_text, payload.website_url, payload.email, payload.phone, payload.payment_id, payload.recruiter_name]):
        raise HTTPException(
            status_code=400,
            detail="Investigation submission must contain at least one field (offer text, URL, contact, or payment ID).",
        )

    case_num = f"SG-{datetime.utcnow().strftime('%Y')}-{uuid.uuid4().hex[:6].upper()}"
    title = payload.title or f"Investigation: {payload.recruiter_name or payload.website_url or 'Suspicious Offer'}"

    # Stage 1 & 2: Record Creation
    inv = Investigation(
        case_number=case_num,
        title=title,
        raw_text=payload.raw_text,
        submitter_notes=payload.notes,
        status=InvestigationStatus.UNDER_REVIEW.value,
        overall_risk_score=0.0,
        confidence_level="LOW",
        summary="Processing investigation...",
    )
    db.add(inv)
    db.flush()

    events: List[InvestigationEvent] = []

    def record_event(stage: str, msg: str, details: Optional[Dict[str, Any]] = None):
        ev = InvestigationEvent(
            investigation_id=inv.id,
            event_stage=stage,
            message=msg,
            details_json=json.dumps(details) if details else None,
        )
        db.add(ev)
        events.append(ev)

    record_event("VALIDATION", "Validating and normalizing submitted indicators.")

    # Stage 3: Scam Pattern Analysis Engine
    analysis = scam_engine.analyze(
        text=payload.raw_text,
        website_url=payload.website_url,
        recruiter_name=payload.recruiter_name,
        email=payload.email,
        phone=payload.phone,
        payment_id=payload.payment_id,
        notes=payload.notes,
    )
    record_event("PATTERN_ANALYSIS", f"Scam detection engine evaluated content across 8 vectors. Score: {analysis['overall_risk_score']}/100.")

    # Stage 4: Extract and Normalize Digital Indicators -> Create Entities
    created_entities: List[Entity] = []

    # A. Root Job Offer Node
    job_label = (payload.recruiter_name or "Offer") + f" [Case {case_num}]"
    job_entity = Entity(
        investigation_id=inv.id,
        entity_type=EntityType.JOB_OFFER.value,
        raw_value=payload.raw_text[:300] if payload.raw_text else title,
        normalized_value=(payload.raw_text[:200] if payload.raw_text else title).lower(),
        display_label=job_label,
        risk_score=analysis["overall_risk_score"],
    )
    db.add(job_entity)
    created_entities.append(job_entity)

    # B. Domain / URL
    if payload.website_url:
        try:
            norm_url, norm_dom = normalizer.validate_and_normalize_url(payload.website_url)
            dom_entity = Entity(
                investigation_id=inv.id,
                entity_type=EntityType.DOMAIN.value,
                raw_value=payload.website_url,
                normalized_value=norm_dom,
                display_label=norm_dom,
                risk_score=min(100.0, analysis["overall_risk_score"] + 10.0),
            )
            db.add(dom_entity)
            created_entities.append(dom_entity)
        except (ValueError, SSRFValidationError) as exc:
            record_event("SECURITY_WARNING", f"URL parsing warning: {str(exc)}")

    # C. Email
    if payload.email:
        norm_em = normalizer.normalize_email(payload.email)
        if norm_em:
            em_entity = Entity(
                investigation_id=inv.id,
                entity_type=EntityType.EMAIL.value,
                raw_value=payload.email,
                normalized_value=norm_em,
                display_label=norm_em,
                risk_score=analysis["overall_risk_score"],
            )
            db.add(em_entity)
            created_entities.append(em_entity)

    # D. Phone
    if payload.phone:
        norm_ph = normalizer.normalize_phone(payload.phone)
        if norm_ph:
            ph_entity = Entity(
                investigation_id=inv.id,
                entity_type=EntityType.PHONE.value,
                raw_value=payload.phone,
                normalized_value=norm_ph,
                display_label=norm_ph,
                risk_score=analysis["overall_risk_score"],
            )
            db.add(ph_entity)
            created_entities.append(ph_entity)

    # E. Payment ID
    if payload.payment_id:
        norm_pay = normalizer.normalize_payment_id(payload.payment_id)
        if norm_pay:
            pay_entity = Entity(
                investigation_id=inv.id,
                entity_type=EntityType.PAYMENT_ID.value,
                raw_value=payload.payment_id,
                normalized_value=norm_pay,
                display_label=f"Payment: {norm_pay}",
                risk_score=95.0,
            )
            db.add(pay_entity)
            created_entities.append(pay_entity)

    # F. Recruiter Persona
    if payload.recruiter_name:
        rec_clean = payload.recruiter_name.strip()
        rec_entity = Entity(
            investigation_id=inv.id,
            entity_type=EntityType.RECRUITER.value,
            raw_value=rec_clean,
            normalized_value=rec_clean.lower(),
            display_label=f"Recruiter: {rec_clean}",
            risk_score=analysis["overall_risk_score"],
        )
        db.add(rec_entity)
        created_entities.append(rec_entity)

    db.flush()
    record_event("INDICATOR_EXTRACTION", f"Extracted and normalized {len(created_entities)} digital indicator entities.")

    # Internal edges linking indicators to this job offer
    for e in created_entities:
        if e.id != job_entity.id:
            db.add(
                Relationship(
                    source_entity_id=job_entity.id,
                    target_entity_id=e.id,
                    relationship_type=RelationshipType.OFFER_PROPAGATOR.value,
                    confidence=0.90,
                    matching_indicator=e.normalized_value,
                    evidence_reason=f"Indicator directly cited in investigation submission {case_num}.",
                )
            )

    # Stage 5: External Intelligence via TinyFish
    if payload.website_url:
        record_event("WEB_INTEL", "Checking external public web intelligence via TinyFish adapter.")
        tiny_res = await tinyfish_service.investigate_website(payload.website_url)
        if tiny_res.get("success") and tiny_res.get("evidence"):
            ev_data = tiny_res["evidence"]
            db.add(
                EvidenceSource(
                    investigation_id=inv.id,
                    source_type=EvidenceSourceType.TINYFISH_WEB_RESEARCH.value,
                    source_url=ev_data["url"],
                    page_title=ev_data["page_title"],
                    raw_content_preview=ev_data.get("raw_content", "")[:500],
                    claims_supported=ev_data.get("claims", "Public web reconnaissance"),
                    is_verified=True,
                )
            )
            record_event("WEB_INTEL", "TinyFish live reconnaissance completed and preserved.")
        else:
            record_event("WEB_INTEL", tiny_res.get("message", "TinyFish lookup finished with fallback."))
    else:
        record_event("WEB_INTEL", "No URL provided; skipped live web crawling.")

    # Save Indicators from Analysis
    for ind in analysis["detected_indicators"]:
        db.add(
            Indicator(
                investigation_id=inv.id,
                indicator_category=ind["category"],
                title=ind["title"],
                severity=ind["severity"],
                matched_snippet=ind.get("snippet"),
                explanation=ind["explanation"],
                weight=ind.get("weight", 1.0),
            )
        )

    # Stage 6, 7 & 8: Historical Evidence Correlation & Relationship Detection
    record_event("GRAPH_CORRELATION", "Correlating extracted indicators against database of historical scam entities.")
    matched_relationships = relationship_engine.correlate_investigation(
        db=db,
        current_investigation_id=inv.id,
        entities_created=created_entities,
        offer_text=payload.raw_text,
    )
    if matched_relationships:
        record_event(
            "RELATIONSHIP_BUILDING",
            f"DISCOVERY: Connected to {len(matched_relationships)} existing entity relationships across other investigations!",
            details={"connections_count": len(matched_relationships)},
        )
    else:
        record_event("RELATIONSHIP_BUILDING", "No cross-investigation matches found. Entity established as isolated node.")

    # Stage 9: Generate Analysis Result
    ar = AnalysisResult(
        investigation_id=inv.id,
        risk_verdict=analysis["risk_verdict"],
        overall_risk_score=analysis["overall_risk_score"],
        detected_indicators_json=json.dumps(analysis["detected_indicators"]),
        exact_snippets_json=json.dumps(analysis["exact_snippets"]),
        missing_inconsistent_info_json=json.dumps(analysis["missing_inconsistencies"]),
        recommended_verification_steps_json=json.dumps(analysis["recommended_verification_steps"]),
        confidence_explanation=analysis["confidence_explanation"],
        limitations_and_uncertainty=analysis["limitations_and_uncertainty"],
        ai_engine_used=analysis["ai_engine_used"],
    )
    db.add(ar)

    # Stage 10: Generate Tailored Recommended Actions
    safety_plan = safety_service.generate_recommendations(
        has_paid=bool(payload.payment_id and ("paid" in (payload.notes or "").lower() or "sent" in (payload.notes or "").lower())),
        shared_otp="otp" in (payload.raw_text or "").lower() or "password" in (payload.raw_text or "").lower(),
        shared_id="aadhaar" in (payload.raw_text or "").lower() or "pan" in (payload.raw_text or "").lower(),
        clicked_link=bool(payload.website_url),
    )

    for act in safety_plan["actions"]:
        db.add(
            RecommendedAction(
                investigation_id=inv.id,
                scenario_type="AUTO_ASSESSMENT",
                priority=act["priority"],
                title=act["title"],
                description=act["description"],
                official_portal_url=act.get("portal_url"),
                official_portal_name=act.get("portal_name"),
                helpline_number=act.get("helpline"),
            )
        )

    # Update Investigation Master Status & Risk
    inv.overall_risk_score = analysis["overall_risk_score"]
    inv.confidence_level = analysis["confidence_level"]
    inv.status = (
        InvestigationStatus.CONFIRMED_SCAM.value if analysis["overall_risk_score"] >= 65.0
        else (InvestigationStatus.SUSPICIOUS.value if analysis["overall_risk_score"] >= 35.0
              else InvestigationStatus.BENIGN.value)
    )
    inv.summary = analysis["summary"]

    record_event("COMPLETED", f"Investigation finalized. Verdict: {inv.status} with Risk: {inv.overall_risk_score}/100.")
    db.commit()
    db.refresh(inv)

    return get_investigation_detail(inv.id, db)


@router.get("/{investigation_id}", response_model=InvestigationDetail)
def get_investigation_detail(investigation_id: int, db: Session = Depends(get_db)):
    """Retrieves full investigation dossier including entities, indicators, evidence, and events."""
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail=f"Investigation with ID {investigation_id} not found.")

    analysis_resp = None
    if inv.analysis_results:
        ar = inv.analysis_results
        analysis_resp = AnalysisResultResponse(
            risk_verdict=ar.risk_verdict,
            overall_risk_score=ar.overall_risk_score,
            detected_indicators=json.loads(ar.detected_indicators_json or "[]"),
            exact_snippets=json.loads(ar.exact_snippets_json or "{}"),
            missing_inconsistencies=json.loads(ar.missing_inconsistent_info_json or "[]"),
            recommended_verification_steps=json.loads(ar.recommended_verification_steps_json or "[]"),
            confidence_explanation=ar.confidence_explanation,
            limitations_and_uncertainty=ar.limitations_and_uncertainty,
            ai_engine_used=ar.ai_engine_used,
        )

    events_resp = [
        InvestigationProgressEvent(
            stage=ev.event_stage,
            message=ev.message,
            details=json.loads(ev.details_json) if ev.details_json else None,
            timestamp=ev.timestamp,
        )
        for ev in inv.events
    ]

    return InvestigationDetail(
        id=inv.id,
        case_number=inv.case_number,
        title=inv.title,
        raw_text=inv.raw_text,
        submitter_notes=inv.submitter_notes,
        status=inv.status,
        overall_risk_score=inv.overall_risk_score,
        confidence_level=inv.confidence_level,
        summary=inv.summary,
        created_at=inv.created_at,
        updated_at=inv.updated_at,
        entities=[EntityResponse.model_validate(e) for e in inv.entities],
        indicators=[
            IndicatorResponse(
                id=i.id,
                category=i.indicator_category,
                title=i.title,
                severity=i.severity,
                matched_snippet=i.matched_snippet,
                explanation=i.explanation,
                weight=i.weight,
            )
            for i in inv.indicators
        ],
        evidence_sources=[EvidenceSourceResponse.model_validate(ev) for ev in inv.evidence_sources],
        analysis_results=analysis_resp,
        events=events_resp,
    )


@router.delete("/{investigation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investigation(investigation_id: int, db: Session = Depends(get_db)):
    """Deletes an investigation and cascades deletion to associated entities, relationships, and evidence."""
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    db.delete(inv)
    db.commit()
    return None
