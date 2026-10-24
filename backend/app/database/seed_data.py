"""
ScamGraph AI - Seed Data Generator
Pre-populates the database with realistic, clearly labeled sample investigations demonstrating:
1. Syndicate Alpha: Impersonating TCS Careers using fake domain 'tcs-careers-portal.online', Telegram bot, and shared UPI 'hr.recruit@axisbank'
2. Syndicate Alpha (Second Case): Fake Infosys hiring offer sharing the exact same UPI 'hr.recruit@axisbank' and phone '+919876543210'
3. Syndicate Beta: Task-based YouTube video rating scam with domain 'work-task-earn.xyz' and WhatsApp recruiter
4. Case 4: Isolated / Benign campus placement communication (demonstrates unconnected entity handling)
All records are marked with '[SAMPLE DATA]' in title and provenance.
"""

from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from app.models.investigation import (
    Investigation,
    InvestigationStatus,
    Entity,
    EntityType,
    Indicator,
    SeverityLevel,
    Relationship,
    RelationshipType,
    EvidenceSource,
    EvidenceSourceType,
    AnalysisResult,
    RecommendedAction,
    InvestigationEvent,
)
from app.services.relationship_engine import relationship_engine


def seed_sample_investigations(db: Session) -> None:
    """Populates realistic cyber investigation cases if database is empty."""
    if db.query(Investigation).count() > 0:
        return  # Database already seeded or populated

    now = datetime.utcnow()

    # =========================================================================
    # CASE 1: Syndicate Alpha - Fake TCS Recruitment Portal
    # =========================================================================
    case1 = Investigation(
        case_number="SG-2026-001",
        title="[SAMPLE DATA] Fake TCS Direct Hiring & Security Deposit Scam",
        raw_text=(
            "Dear Candidate, Congratulations! You have been shortlisted for Software Developer at Tata Consultancy Services (TCS). "
            "Package: Rs 8.5 LPA. No technical interview required. Direct joining letter attached. "
            "To confirm your slot, transfer mandatory refundable security deposit of Rs 4,999/- within 24 hours to UPI ID: hr.recruit@axisbank. "
            "Send payment screenshot on Telegram: @tcs_hr_onboarding. Failure to pay will lead to permanent blacklisting under legal employment terms."
        ),
        submitter_notes="Received via unsolicited SMS and WhatsApp from +919876543210. Link points to tcs-careers-portal.online",
        status=InvestigationStatus.CONFIRMED_SCAM.value,
        overall_risk_score=92.5,
        confidence_level="HIGH",
        summary="High-severity employment fraud campaign impersonating Tata Consultancy Services. Solicits Rs 4,999 refundable deposit to personal UPI ID, utilizes legal threats and artificial 24-hr deadline.",
        created_at=now - timedelta(days=4),
        updated_at=now - timedelta(days=4),
    )
    db.add(case1)
    db.flush()

    # Entities for Case 1
    e1_job = Entity(
        investigation_id=case1.id,
        entity_type=EntityType.JOB_OFFER.value,
        raw_value=case1.raw_text[:200],
        normalized_value="tcs software developer direct selection 8.5 lpa",
        display_label="TCS Direct Selection Offer",
        risk_score=95.0,
        has_geocoding=True,
        latitude=19.0760,
        longitude=72.8777,
        country="India",
        city="Mumbai",
    )
    e1_domain = Entity(
        investigation_id=case1.id,
        entity_type=EntityType.DOMAIN.value,
        raw_value="https://tcs-careers-portal.online",
        normalized_value="tcs-careers-portal.online",
        display_label="tcs-careers-portal.online",
        risk_score=88.0,
        has_geocoding=True,
        latitude=28.6139,
        longitude=77.2090,
        country="India",
        city="New Delhi",
    )
    e1_email = Entity(
        investigation_id=case1.id,
        entity_type=EntityType.EMAIL.value,
        raw_value="tcs.careers.helpdesk@gmail.com",
        normalized_value="tcs.careers.helpdesk@gmail.com",
        display_label="tcs.careers.helpdesk@gmail.com",
        risk_score=75.0,
    )
    e1_phone = Entity(
        investigation_id=case1.id,
        entity_type=EntityType.PHONE.value,
        raw_value="+91 98765 43210",
        normalized_value="+919876543210",
        display_label="+91 98765 43210",
        risk_score=85.0,
    )
    e1_upi = Entity(
        investigation_id=case1.id,
        entity_type=EntityType.PAYMENT_ID.value,
        raw_value="hr.recruit@axisbank",
        normalized_value="hr.recruit@axisbank",
        display_label="UPI: hr.recruit@axisbank",
        risk_score=98.0,
    )
    e1_telegram = Entity(
        investigation_id=case1.id,
        entity_type=EntityType.TELEGRAM.value,
        raw_value="@tcs_hr_onboarding",
        normalized_value="tcs_hr_onboarding",
        display_label="@tcs_hr_onboarding",
        risk_score=70.0,
    )
    db.add_all([e1_job, e1_domain, e1_email, e1_phone, e1_upi, e1_telegram])
    db.flush()

    # Indicators for Case 1
    ind1 = Indicator(
        investigation_id=case1.id,
        indicator_category="UPFRONT_PAYMENT_DEMAND",
        title="Refundable Security Deposit Demand (Rs 4,999)",
        severity=SeverityLevel.CRITICAL.value,
        matched_snippet="transfer mandatory refundable security deposit of Rs 4,999/-",
        explanation="Legitimate corporate recruitment never demands upfront payments or refundable security fees.",
        weight=35.0,
    )
    ind2 = Indicator(
        investigation_id=case1.id,
        indicator_category="URGENT_DEMAND",
        title="Artificial 24-Hour Time Pressure",
        severity=SeverityLevel.HIGH.value,
        matched_snippet="within 24 hours to UPI ID: hr.recruit@axisbank",
        explanation="Coercive urgency tactic used to force payment before the victim can independently verify.",
        weight=20.0,
    )
    ind3 = Indicator(
        investigation_id=case1.id,
        indicator_category="COERCION_OR_THREAT",
        title="Blacklisting / Legal Threat Language",
        severity=SeverityLevel.HIGH.value,
        matched_snippet="lead to permanent blacklisting under legal employment terms",
        explanation="Predatory intimidation designed to panic young job seekers into compliance.",
        weight=25.0,
    )
    db.add_all([ind1, ind2, ind3])

    # Analysis Result for Case 1
    ar1 = AnalysisResult(
        investigation_id=case1.id,
        risk_verdict="CONFIRMED_SCAM_PATTERNS",
        overall_risk_score=92.5,
        detected_indicators_json=json.dumps(["UPFRONT_PAYMENT_DEMAND", "URGENT_DEMAND", "COERCION_OR_THREAT", "INCONSISTENT_RECRUITER_DOMAIN"]),
        exact_snippets_json=json.dumps({"deposit": "Rs 4,999", "deadline": "within 24 hours"}),
        missing_inconsistent_info_json=json.dumps(["Claimed TCS brand but using free @gmail.com address", "Personal UPI destination rather than corporate merchant gateway"]),
        recommended_verification_steps_json=json.dumps(["Cross-check candidate registration on TCS NextStep portal (nextstep.tcs.com)", "Call 1930 Helpline if payment was already made"]),
        confidence_explanation="Multiple documented critical threat vectors detected: advance fee demand, personal UPI recipient, and coercive intimidation.",
        limitations_and_uncertainty="Analysis based on submitter-provided message; confirmed against historical spam patterns.",
    )
    db.add(ar1)

    # Internal links for Case 1 (Offer connected to its indicators)
    db.add_all([
        Relationship(source_entity_id=e1_job.id, target_entity_id=e1_domain.id, relationship_type=RelationshipType.HOSTED_ON.value, confidence=0.95, matching_indicator="tcs-careers-portal.online", evidence_reason="Recruitment application portal hosted on external domain"),
        Relationship(source_entity_id=e1_job.id, target_entity_id=e1_upi.id, relationship_type=RelationshipType.PAYMENT_RECIPIENT.value, confidence=0.99, matching_indicator="hr.recruit@axisbank", evidence_reason="Job offer explicitly instructs victim to transfer Rs 4,999 to this UPI ID"),
        Relationship(source_entity_id=e1_job.id, target_entity_id=e1_phone.id, relationship_type=RelationshipType.OFFER_PROPAGATOR.value, confidence=0.90, matching_indicator="+919876543210", evidence_reason="Offer text dispatched and negotiated via this telephone handle"),
    ])

    # =========================================================================
    # CASE 2: Syndicate Alpha (Connected Campaign) - Fake Infosys Onboarding
    # SHARES SAME UPI ('hr.recruit@axisbank') and PHONE ('+919876543210')
    # =========================================================================
    case2 = Investigation(
        case_number="SG-2026-002",
        title="[SAMPLE DATA] Fake Infosys Remote Internship Kit Scam",
        raw_text=(
            "Infosys Virtual Internship Program 2026: You are selected for Summer Web Development Internship. "
            "Stipend: Rs 30,000/month. Free laptop and training kit will be dispatched to your address. "
            "Mandatory courier and insurance clearance charge of Rs 3,500/- required prior to dispatch. "
            "Send payment immediately to UPI: hr.recruit@axisbank or contact HR Desk at +919876543210."
        ),
        submitter_notes="Received via college student Telegram group. Promising free laptop after paying courier fee.",
        status=InvestigationStatus.CONFIRMED_SCAM.value,
        overall_risk_score=87.0,
        confidence_level="HIGH",
        summary="Internship advance-fee fraud mimicking Infosys. Requests courier clearance fee to the exact same UPI handle observed in Case SG-2026-001.",
        created_at=now - timedelta(days=2),
        updated_at=now - timedelta(days=2),
    )
    db.add(case2)
    db.flush()

    e2_job = Entity(
        investigation_id=case2.id,
        entity_type=EntityType.JOB_OFFER.value,
        raw_value=case2.raw_text[:200],
        normalized_value="infosys virtual internship program summer web dev stipend 30000",
        display_label="Infosys Virtual Internship Offer",
        risk_score=89.0,
        has_geocoding=True,
        latitude=12.9716,
        longitude=77.5946,
        country="India",
        city="Bengaluru",
    )
    e2_upi = Entity(
        investigation_id=case2.id,
        entity_type=EntityType.PAYMENT_ID.value,
        raw_value="hr.recruit@axisbank",
        normalized_value="hr.recruit@axisbank",
        display_label="UPI: hr.recruit@axisbank",
        risk_score=98.0,
    )
    e2_phone = Entity(
        investigation_id=case2.id,
        entity_type=EntityType.PHONE.value,
        raw_value="+91 98765 43210",
        normalized_value="+919876543210",
        display_label="+91 98765 43210",
        risk_score=85.0,
    )
    e2_email = Entity(
        investigation_id=case2.id,
        entity_type=EntityType.EMAIL.value,
        raw_value="infosys.internship.onboard@outlook.com",
        normalized_value="infosys.internship.onboard@outlook.com",
        display_label="infosys.internship.onboard@outlook.com",
        risk_score=70.0,
    )
    db.add_all([e2_job, e2_upi, e2_phone, e2_email])
    db.flush()

    # Link Case 2 entities internally
    db.add_all([
        Relationship(source_entity_id=e2_job.id, target_entity_id=e2_upi.id, relationship_type=RelationshipType.PAYMENT_RECIPIENT.value, confidence=0.98, matching_indicator="hr.recruit@axisbank", evidence_reason="Offer requires Rs 3,500 courier fee sent to this UPI"),
        Relationship(source_entity_id=e2_job.id, target_entity_id=e2_phone.id, relationship_type=RelationshipType.OFFER_PROPAGATOR.value, confidence=0.90, matching_indicator="+919876543210", evidence_reason="Contact number provided for internship verification"),
    ])

    # CROSS-CASE RELATIONSHIPS (Syndicate Alpha Linkages!)
    db.add_all([
        Relationship(
            source_entity_id=e1_upi.id,
            target_entity_id=e2_upi.id,
            relationship_type=RelationshipType.SAME_PAYMENT_ID.value,
            confidence=0.98,
            matching_indicator="hr.recruit@axisbank",
            evidence_reason="CRITICAL SYNDICATE CORRELATION: Identical UPI payment destination 'hr.recruit@axisbank' utilized across both TCS scam (SG-2026-001) and Infosys scam (SG-2026-002).",
        ),
        Relationship(
            source_entity_id=e1_phone.id,
            target_entity_id=e2_phone.id,
            relationship_type=RelationshipType.SAME_PHONE.value,
            confidence=0.92,
            matching_indicator="+919876543210",
            evidence_reason="Identical mobile phone number '+919876543210' shared between both recruitment operations.",
        ),
    ])

    # =========================================================================
    # CASE 3: Syndicate Beta - YouTube Video Task / Crypto Scheme
    # =========================================================================
    case3 = Investigation(
        case_number="SG-2026-003",
        title="[SAMPLE DATA] Part-Time YouTube Review Task Scam (Work-Task-Earn)",
        raw_text=(
            "Hello! I am Sarah from Global Media Marketing. We are hiring part-time freelancers to review YouTube videos. "
            "Earn Rs 2,500 to Rs 8,000 daily from home. Complete 3 demo tasks on our portal: https://work-task-earn.xyz. "
            "To unlock Level-2 high earning commissions, deposit Rs 2,000 activation fee via UPI: taskmaster@ybl or USDT wallet."
        ),
        submitter_notes="Received via unsolicited WhatsApp message from unknown international number.",
        status=InvestigationStatus.CONFIRMED_SCAM.value,
        overall_risk_score=78.0,
        confidence_level="HIGH",
        summary="Task-based Ponzi scam leveraging fake social media liking tasks. Requires advance deposit to unlock VIP payout tiers.",
        created_at=now - timedelta(days=1),
        updated_at=now - timedelta(days=1),
    )
    db.add(case3)
    db.flush()

    e3_job = Entity(
        investigation_id=case3.id,
        entity_type=EntityType.JOB_OFFER.value,
        raw_value=case3.raw_text[:200],
        normalized_value="part-time youtube review earn 2500 to 8000 daily deposit 2000",
        display_label="YouTube Rating Task Job",
        risk_score=80.0,
        has_geocoding=True,
        latitude=1.3521,
        longitude=103.8198,
        country="Singapore",
        city="Singapore",
    )
    e3_domain = Entity(
        investigation_id=case3.id,
        entity_type=EntityType.DOMAIN.value,
        raw_value="https://work-task-earn.xyz",
        normalized_value="work-task-earn.xyz",
        display_label="work-task-earn.xyz",
        risk_score=85.0,
        has_geocoding=True,
        latitude=37.7749,
        longitude=-122.4194,
        country="United States",
        city="San Francisco",
    )
    e3_upi = Entity(
        investigation_id=case3.id,
        entity_type=EntityType.PAYMENT_ID.value,
        raw_value="taskmaster@ybl",
        normalized_value="taskmaster@ybl",
        display_label="UPI: taskmaster@ybl",
        risk_score=88.0,
    )
    db.add_all([e3_job, e3_domain, e3_upi])
    db.flush()

    db.add_all([
        Relationship(source_entity_id=e3_job.id, target_entity_id=e3_domain.id, relationship_type=RelationshipType.HOSTED_ON.value, confidence=0.95, matching_indicator="work-task-earn.xyz", evidence_reason="Task portal hosted on high-risk .xyz TLD"),
        Relationship(source_entity_id=e3_job.id, target_entity_id=e3_upi.id, relationship_type=RelationshipType.PAYMENT_RECIPIENT.value, confidence=0.92, matching_indicator="taskmaster@ybl", evidence_reason="Level-2 tier activation fee transferred to this UPI address"),
    ])

    # =========================================================================
    # CASE 4: BENIGN / ISOLATED SAMPLE - Authentic Campus Placement Notice
    # Demonstrates unconnected entity handling and 0-link integrity
    # =========================================================================
    case4 = Investigation(
        case_number="SG-2026-004",
        title="[SAMPLE DATA] Authentic College Placement Notification (Benign)",
        raw_text=(
            "Notice to Final Year B.Tech students: Campus placement drive for Capgemini will be conducted on 15th November. "
            "Please register through official college intranet portal. No registration fee is charged. "
            "Official queries: placement@rbmi.edu.in. Contact training and placement cell, Block A."
        ),
        submitter_notes="Verified notice issued by official college placement office.",
        status=InvestigationStatus.BENIGN.value,
        overall_risk_score=5.0,
        confidence_level="HIGH",
        summary="Legitimate institutional recruitment announcement. No financial requests, uses verified institutional domain (.edu.in), zero scam threat indicators.",
        created_at=now,
        updated_at=now,
    )
    db.add(case4)
    db.flush()

    e4_job = Entity(
        investigation_id=case4.id,
        entity_type=EntityType.JOB_OFFER.value,
        raw_value="Notice to Final Year students: Capgemini campus placement",
        normalized_value="capgemini campus placement drive final year official intranet",
        display_label="Campus Placement Drive Notice",
        risk_score=5.0,
        has_geocoding=True,
        latitude=28.3670,
        longitude=79.4304,
        country="India",
        city="Bareilly",
    )
    e4_email = Entity(
        investigation_id=case4.id,
        entity_type=EntityType.EMAIL.value,
        raw_value="placement@rbmi.edu.in",
        normalized_value="placement@rbmi.edu.in",
        display_label="placement@rbmi.edu.in",
        risk_score=2.0,
    )
    db.add_all([e4_job, e4_email])
    db.flush()

    # Note: Case 4 intentionally has NO cross-case relationships, verifying isolated node handling!

    db.commit()
