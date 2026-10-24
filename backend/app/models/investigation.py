"""
ScamGraph AI - Database Models
SQLAlchemy Declarative Models for Investigations, Entities, Indicators, Relationships,
Evidence Sources, Analysis Results, Recommended Actions, and Events.
"""

from datetime import datetime
from typing import Optional, List
import enum
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, Enum, Index
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class InvestigationStatus(str, enum.Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    SUSPICIOUS = "SUSPICIOUS"
    CONFIRMED_SCAM = "CONFIRMED_SCAM"
    BENIGN = "BENIGN"
    CLOSED = "CLOSED"


class SeverityLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EntityType(str, enum.Enum):
    JOB_OFFER = "JOB_OFFER"
    DOMAIN = "DOMAIN"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    PAYMENT_ID = "PAYMENT_ID"
    RECRUITER = "RECRUITER"
    ORGANIZATION = "ORGANIZATION"
    TELEGRAM = "TELEGRAM"
    WHATSAPP = "WHATSAPP"
    OTHER = "OTHER"


class RelationshipType(str, enum.Enum):
    SAME_DOMAIN = "SAME_DOMAIN"
    SAME_EMAIL = "SAME_EMAIL"
    SAME_PHONE = "SAME_PHONE"
    SAME_PAYMENT_ID = "SAME_PAYMENT_ID"
    SIMILAR_CONTENT = "SIMILAR_CONTENT"
    SHARED_RECRUITER = "SHARED_RECRUITER"
    OFFER_PROPAGATOR = "OFFER_PROPAGATOR"
    PAYMENT_RECIPIENT = "PAYMENT_RECIPIENT"
    HOSTED_ON = "HOSTED_ON"
    OTHER = "OTHER"


class EvidenceSourceType(str, enum.Enum):
    USER_SUBMISSION = "USER_SUBMISSION"
    TINYFISH_WEB_RESEARCH = "TINYFISH_WEB_RESEARCH"
    WHOIS_DNS = "WHOIS_DNS"
    COMPANY_REGISTRY = "COMPANY_REGISTRY"
    OFFICIAL_ADVISORY = "OFFICIAL_ADVISORY"


class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    case_number = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=True)
    submitter_notes = Column(Text, nullable=True)
    status = Column(String(32), default=InvestigationStatus.OPEN.value, nullable=False)
    overall_risk_score = Column(Float, default=0.0)  # 0 to 100
    confidence_level = Column(String(32), default="LOW")  # LOW, MEDIUM, HIGH
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    entities = relationship("Entity", back_populates="investigation", cascade="all, delete-orphan")
    indicators = relationship("Indicator", back_populates="investigation", cascade="all, delete-orphan")
    evidence_sources = relationship("EvidenceSource", back_populates="investigation", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="investigation", uselist=False, cascade="all, delete-orphan")
    recommended_actions = relationship("RecommendedAction", back_populates="investigation", cascade="all, delete-orphan")
    events = relationship("InvestigationEvent", back_populates="investigation", cascade="all, delete-orphan")


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(32), nullable=False, index=True)
    raw_value = Column(String(512), nullable=False)
    normalized_value = Column(String(512), nullable=False, index=True)
    display_label = Column(String(255), nullable=False)
    risk_score = Column(Float, default=0.0)
    
    # Geolocation if supported by evidence (latitude, longitude, country, city)
    has_geocoding = Column(Boolean, default=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)

    metadata_json = Column(Text, nullable=True)  # JSON-encoded extra attributes
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    investigation = relationship("Investigation", back_populates="entities")
    outgoing_relationships = relationship(
        "Relationship", foreign_keys="Relationship.source_entity_id", back_populates="source_entity", cascade="all, delete-orphan"
    )
    incoming_relationships = relationship(
        "Relationship", foreign_keys="Relationship.target_entity_id", back_populates="target_entity", cascade="all, delete-orphan"
    )


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    indicator_category = Column(String(64), nullable=False)  # e.g. UPFRONT_PAYMENT, URGENT_DEMAND, LOOKALIKE_DOMAIN
    title = Column(String(255), nullable=False)
    severity = Column(String(32), default=SeverityLevel.MEDIUM.value, nullable=False)
    matched_snippet = Column(Text, nullable=True)
    explanation = Column(Text, nullable=False)
    weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    investigation = relationship("Investigation", back_populates="indicators")


class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_entity_id = Column(Integer, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    target_entity_id = Column(Integer, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type = Column(String(64), nullable=False)  # SAME_DOMAIN, SAME_EMAIL, etc.
    confidence = Column(Float, default=1.0)  # 0.0 to 1.0
    matching_indicator = Column(String(255), nullable=False)  # The normalized token that matched
    evidence_reason = Column(Text, nullable=False)  # Human-readable explanation of why linked
    evidence_source_id = Column(Integer, ForeignKey("evidence_sources.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    source_entity = relationship("Entity", foreign_keys=[source_entity_id], back_populates="outgoing_relationships")
    target_entity = relationship("Entity", foreign_keys=[target_entity_id], back_populates="incoming_relationships")
    evidence_source = relationship("EvidenceSource")


class EvidenceSource(Base):
    __tablename__ = "evidence_sources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type = Column(String(64), nullable=False)  # EvidenceSourceType
    source_url = Column(String(1024), nullable=True)
    page_title = Column(String(512), nullable=True)
    retrieval_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    raw_content_preview = Column(Text, nullable=True)
    claims_supported = Column(Text, nullable=True)  # JSON or text of claims supported
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    investigation = relationship("Investigation", back_populates="evidence_sources")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    risk_verdict = Column(String(64), nullable=False)  # HIGH_RISK, MEDIUM_RISK, SUSPICIOUS, UNVERIFIED, SAFE
    overall_risk_score = Column(Float, default=0.0)
    detected_indicators_json = Column(Text, nullable=True)  # JSON list
    exact_snippets_json = Column(Text, nullable=True)  # JSON dict
    missing_inconsistent_info_json = Column(Text, nullable=True)  # JSON list
    recommended_verification_steps_json = Column(Text, nullable=True)  # JSON list
    confidence_explanation = Column(Text, nullable=True)
    limitations_and_uncertainty = Column(Text, nullable=True)
    ai_engine_used = Column(String(64), default="rule-engine-v2")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    investigation = relationship("Investigation", back_populates="analysis_results")


class RecommendedAction(Base):
    __tablename__ = "recommended_actions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_type = Column(String(64), nullable=False)  # NOT_PAID, PAID, SHARED_OTP, SHARED_ID, CLICKED_LINK, GENERAL
    priority = Column(String(32), default="HIGH")  # CRITICAL, HIGH, MEDIUM, LOW
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    official_portal_url = Column(String(512), nullable=True)
    official_portal_name = Column(String(255), nullable=True)
    helpline_number = Column(String(64), nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    investigation = relationship("Investigation", back_populates="recommended_actions")


class InvestigationEvent(Base):
    __tablename__ = "investigation_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    event_stage = Column(String(64), nullable=False)  # e.g. VALIDATION, PATTERN_ANALYSIS, GRAPH_LINKING
    message = Column(String(512), nullable=False)
    details_json = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    investigation = relationship("Investigation", back_populates="events")


# Helpful composite indexes for high-speed graph traversals
Index("idx_entity_norm_val", Entity.normalized_value, Entity.entity_type)
Index("idx_rel_src_tgt", Relationship.source_entity_id, Relationship.target_entity_id)
