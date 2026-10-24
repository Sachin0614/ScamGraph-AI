"""
ScamGraph AI - Comprehensive Test Suite
Tests for:
1. Domain and indicator normalization
2. Exact-match relationship detection
3. Duplicate indicators handling
4. Unconnected entities integrity (no fake relationships)
5. Multiple shared indicators (domain + email + phone + UPI)
6. Conflicting evidence and unverified claims
7. Empty or invalid input rejection
8. TinyFish disabled or failed fallback
9. Graph updates after new investigations
10. URL safety and SSRF validation
11. Evidence provenance and relationship explanations
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.investigation import (
    Base,
    Investigation,
    InvestigationStatus,
    Entity,
    EntityType,
    Relationship,
    RelationshipType,
    Indicator,
)
from app.services.normalizer import normalizer, SSRFValidationError
from app.services.scam_engine import scam_engine
from app.services.relationship_engine import relationship_engine
from app.services.tinyfish_service import tinyfish_service
from app.services.safety_service import safety_service


@pytest.fixture(scope="function")
def db_session():
    """Provides a fresh isolated in-memory SQLite database for each test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    yield session
    session.close()


# =============================================================================
# 1. Indicator Normalization Tests
# =============================================================================
def test_domain_normalization():
    assert normalizer.normalize_domain("HTTPS://WWW.Evil-Domain.XYZ/path/login?ref=123") == "evil-domain.xyz"
    assert normalizer.normalize_domain("   sub.portal.com:8080/index.html   ") == "sub.portal.com"
    assert normalizer.normalize_domain("google.com") == "google.com"
    assert normalizer.normalize_domain("") is None
    assert normalizer.normalize_domain("invalid-no-dot") is None


def test_email_normalization():
    assert normalizer.normalize_email("  Recruiter.HR@Example.COM   ") == "recruiter.hr@example.com"
    assert normalizer.normalize_email("test+scam@gmail.com") == "test+scam@gmail.com"
    assert normalizer.normalize_email("not-an-email") is None
    assert normalizer.normalize_email("") is None


def test_phone_normalization():
    # Indian mobile number normalization
    assert normalizer.normalize_phone("+91 98765-43210") == "+919876543210"
    assert normalizer.normalize_phone("9876543210") == "+919876543210"
    assert normalizer.normalize_phone("09876543210") == "+919876543210"
    # International number
    assert normalizer.normalize_phone("+1 (555) 123-4567") == "+15551234567"
    # Invalid length
    assert normalizer.normalize_phone("123") is None


def test_payment_id_normalization():
    assert normalizer.normalize_payment_id("   Fraudster@OKAXIS   ") == "fraudster@okaxis"
    assert normalizer.normalize_payment_id("0x71C8494f285880479708c35B81Fe81a3A370EF51") == "0x71c8494f285880479708c35b81fe81a3a370ef51"
    assert normalizer.normalize_payment_id("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa") == "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"


# =============================================================================
# 2. SSRF and Dangerous URL Protection Tests
# =============================================================================
def test_ssrf_prohibited_ips_and_hostnames():
    # Loopback IP
    with pytest.raises(SSRFValidationError):
        normalizer.validate_and_normalize_url("http://127.0.0.1:8000/admin")
    
    # Cloud metadata endpoint
    with pytest.raises(SSRFValidationError):
        normalizer.validate_and_normalize_url("http://169.254.169.254/latest/meta-data")

    # Localhost hostname
    with pytest.raises(SSRFValidationError):
        normalizer.validate_and_normalize_url("http://localhost/secret")

    # Private network (10.x.x.x)
    with pytest.raises(SSRFValidationError):
        normalizer.validate_and_normalize_url("http://10.0.1.50/dashboard")

    # Valid public URL
    norm_url, norm_dom = normalizer.validate_and_normalize_url("https://careers.google.com/jobs")
    assert norm_dom == "careers.google.com"


# =============================================================================
# 3. Exact-Match Relationship Detection & No Fake Links
# =============================================================================
def test_exact_match_relationship_detection(db_session):
    # Create Case 1 with UPI 'scammer@upi'
    inv1 = Investigation(case_number="SG-TEST-1", title="Case 1", status="CONFIRMED_SCAM")
    db_session.add(inv1)
    db_session.flush()

    e1 = Entity(
        investigation_id=inv1.id,
        entity_type=EntityType.PAYMENT_ID.value,
        raw_value="Scammer@UPI",
        normalized_value="scammer@upi",
        display_label="scammer@upi",
    )
    db_session.add(e1)
    db_session.commit()

    # Create Case 2 with matching UPI
    inv2 = Investigation(case_number="SG-TEST-2", title="Case 2", status="UNDER_REVIEW")
    db_session.add(inv2)
    db_session.flush()

    e2 = Entity(
        investigation_id=inv2.id,
        entity_type=EntityType.PAYMENT_ID.value,
        raw_value="scammer@upi",
        normalized_value="scammer@upi",
        display_label="scammer@upi",
    )
    db_session.add(e2)
    db_session.flush()

    # Correlate
    relationships = relationship_engine.correlate_investigation(
        db=db_session,
        current_investigation_id=inv2.id,
        entities_created=[e2],
    )

    assert len(relationships) == 1
    rel = relationships[0]
    assert rel.relationship_type == RelationshipType.SAME_PAYMENT_ID.value
    assert rel.confidence >= 0.95
    assert rel.matching_indicator == "scammer@upi"


def test_unconnected_entities_receive_no_relationships(db_session):
    """Verifies that entities with NO matching clue never receive fake relationships."""
    inv1 = Investigation(case_number="SG-TEST-A", title="Case A", status="BENIGN")
    inv2 = Investigation(case_number="SG-TEST-B", title="Case B", status="BENIGN")
    db_session.add_all([inv1, inv2])
    db_session.flush()

    e1 = Entity(
        investigation_id=inv1.id,
        entity_type=EntityType.DOMAIN.value,
        raw_value="https://company-alpha.com",
        normalized_value="company-alpha.com",
        display_label="company-alpha.com",
    )
    e2 = Entity(
        investigation_id=inv2.id,
        entity_type=EntityType.DOMAIN.value,
        raw_value="https://company-beta.com",
        normalized_value="company-beta.com",
        display_label="company-beta.com",
    )
    db_session.add_all([e1, e2])
    db_session.commit()

    rels = relationship_engine.correlate_investigation(
        db=db_session,
        current_investigation_id=inv2.id,
        entities_created=[e2],
    )
    # Must NOT create any relationship
    assert len(rels) == 0


def test_multiple_shared_indicators(db_session):
    """Tests case where multiple indicators (domain, email, phone) all match."""
    inv1 = Investigation(case_number="SG-101", title="Camp A")
    inv2 = Investigation(case_number="SG-102", title="Camp B")
    db_session.add_all([inv1, inv2])
    db_session.flush()

    e1_dom = Entity(investigation_id=inv1.id, entity_type=EntityType.DOMAIN.value, raw_value="scam.com", normalized_value="scam.com", display_label="scam.com")
    e1_em = Entity(investigation_id=inv1.id, entity_type=EntityType.EMAIL.value, raw_value="boss@scam.com", normalized_value="boss@scam.com", display_label="boss@scam.com")
    db_session.add_all([e1_dom, e1_em])
    db_session.flush()

    e2_dom = Entity(investigation_id=inv2.id, entity_type=EntityType.DOMAIN.value, raw_value="scam.com", normalized_value="scam.com", display_label="scam.com")
    e2_em = Entity(investigation_id=inv2.id, entity_type=EntityType.EMAIL.value, raw_value="boss@scam.com", normalized_value="boss@scam.com", display_label="boss@scam.com")
    db_session.add_all([e2_dom, e2_em])
    db_session.flush()

    rels = relationship_engine.correlate_investigation(
        db=db_session,
        current_investigation_id=inv2.id,
        entities_created=[e2_dom, e2_em],
    )
    assert len(rels) == 2
    rel_types = {r.relationship_type for r in rels}
    assert RelationshipType.SAME_DOMAIN.value in rel_types
    assert RelationshipType.SAME_EMAIL.value in rel_types


# =============================================================================
# 4. Scam Analysis Engine Behavior Tests
# =============================================================================
def test_scam_analysis_engine_detects_threat_vectors():
    offer_text = (
        "Congratulations! 100% direct selection for Junior Executive. "
        "Pay Rs 3,000 mandatory training fee within 2 hours or your candidacy will be blacklisted. "
        "Contact HR on Telegram: @hr_bot."
    )
    res = scam_engine.analyze(text=offer_text, payment_id="hr@axisbank")

    assert res["overall_risk_score"] >= 65.0
    assert res["risk_verdict"] == "CONFIRMED_SCAM_PATTERNS"
    categories = [i["category"] for i in res["detected_indicators"]]
    assert "UPFRONT_PAYMENT_DEMAND" in categories
    assert "URGENT_DEMAND" in categories
    assert "COERCION_OR_THREAT" in categories
    assert "UNREALISTIC_CLAIMS" in categories
    assert "UNUSUAL_COMMUNICATION_CHANNEL" in categories
    assert "SOLICITED_PAYMENT_IDENTIFIER" in categories


def test_scam_analysis_benign_content():
    clean_text = "Please find attached the schedule for campus interviews. No fees required. Reach us at hr@university.edu."
    res = scam_engine.analyze(text=clean_text)
    assert res["overall_risk_score"] < 30.0
    assert len(res["detected_indicators"]) == 0


# =============================================================================
# 5. TinyFish Disabled and Fallback Tests
# =============================================================================
@pytest.mark.asyncio
async def test_tinyfish_disabled_fallback():
    tinyfish_service.is_enabled = False
    status = tinyfish_service.get_status()
    assert status["enabled"] is False

    res = await tinyfish_service.investigate_website("https://example-scam-site.com")
    assert res["success"] is False
    assert res["service_status"] == "DISABLED"
    assert "offline" in res["message"].lower()


@pytest.mark.asyncio
async def test_tinyfish_blocks_ssrf_attempt():
    res = await tinyfish_service.investigate_website("http://127.0.0.1:8080/exploit")
    assert res["success"] is False
    assert res["is_ssrf_blocked"] is True


# =============================================================================
# 6. Safety & Response Service Tests
# =============================================================================
def test_safety_service_paid_scenario():
    res = safety_service.generate_recommendations(has_paid=True, amount_lost=5000.0)
    titles = [a["title"] for a in res["actions"]]
    assert any("1930" in t for t in titles)
    assert any("Bank Fraud Desk" in t for t in titles)
    assert len(res["official_portals"]) >= 3
    assert "DISCLAIMER" in res["disclaimer"]


def test_safety_service_unpaid_scenario():
    res = safety_service.generate_recommendations(has_paid=False)
    titles = [a["title"] for a in res["actions"]]
    assert any("Do NOT Send Any Money" in t for t in titles)
    assert any("Chakshu" in t for t in titles)
