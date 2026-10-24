"""
ScamGraph AI - Graph Visualization and Network Analysis Router
Serves 3D globe coordinates, relationship networks, shortest-path calculation,
ego-cluster expansion, and rich entity inspection panels.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.database.session import get_db
from app.models.investigation import (
    Entity,
    Relationship,
    Investigation,
    EvidenceSource,
)
from app.schemas.graph import (
    GraphResponse,
    ShortestPathRequest,
    ShortestPathResponse,
    ClusterExpandResponse,
)
from app.services.relationship_engine import relationship_engine

router = APIRouter(prefix="/graph", tags=["Network Graph"])


@router.get("", response_model=GraphResponse)
def get_network_graph(
    entity_types: Optional[List[str]] = Query(None),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0),
    investigation_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Fetches the 3D Scam Network Graph:
    Includes nodes with 3D spherical positions, evidence-backed edges, cluster metrics, and density.
    """
    data = relationship_engine.get_full_graph_data(
        db=db,
        entity_types=entity_types,
        min_confidence=min_confidence,
        investigation_id=investigation_id,
        search_query=search,
    )
    return data


@router.post("/shortest-path", response_model=ShortestPathResponse)
def get_shortest_relationship_path(
    payload: ShortestPathRequest,
    db: Session = Depends(get_db),
):
    """
    Computes the shortest evidence-backed chain linking two entities across investigations.
    """
    result = relationship_engine.find_shortest_path(
        db=db,
        start_entity_id=payload.start_entity_id,
        end_entity_id=payload.end_entity_id,
    )
    return result


@router.get("/cluster/{entity_id}", response_model=ClusterExpandResponse)
def expand_entity_cluster(
    entity_id: int,
    radius: int = Query(1, ge=1, le=3),
    db: Session = Depends(get_db),
):
    """
    Returns the ego-network / connected cluster around a selected entity.
    """
    result = relationship_engine.expand_cluster(db=db, entity_id=entity_id, radius=radius)
    return result


@router.get("/entity/{entity_id}/details")
def get_entity_inspection_details(
    entity_id: int,
    db: Session = Depends(get_db),
):
    """
    Fulfills Section 9 (Investigation Details Panel):
    When a graph node is selected, returns:
    - Entity type and value
    - Related investigation IDs & titles
    - Matching indicators
    - Connected entities
    - Relationship reasons
    - Evidence source links & timestamps
    - Confidence explanation
    - Available next actions
    """
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    parent_inv = db.query(Investigation).filter(Investigation.id == entity.investigation_id).first()

    # Query outgoing and incoming relationships
    outgoing = (
        db.query(Relationship, Entity)
        .join(Entity, Relationship.target_entity_id == Entity.id)
        .filter(Relationship.source_entity_id == entity.id)
        .all()
    )
    incoming = (
        db.query(Relationship, Entity)
        .join(Entity, Relationship.source_entity_id == Entity.id)
        .filter(Relationship.target_entity_id == entity.id)
        .all()
    )

    connections = []
    for rel, target_ent in outgoing:
        connections.append({
            "direction": "OUTGOING",
            "relationship_id": rel.id,
            "connected_entity_id": target_ent.id,
            "connected_label": target_ent.display_label,
            "connected_type": target_ent.entity_type,
            "relationship_type": rel.relationship_type,
            "confidence": rel.confidence,
            "matching_indicator": rel.matching_indicator,
            "reason": rel.evidence_reason,
            "investigation_id": target_ent.investigation_id,
        })

    for rel, src_ent in incoming:
        connections.append({
            "direction": "INCOMING",
            "relationship_id": rel.id,
            "connected_entity_id": src_ent.id,
            "connected_label": src_ent.display_label,
            "connected_type": src_ent.entity_type,
            "relationship_type": rel.relationship_type,
            "confidence": rel.confidence,
            "matching_indicator": rel.matching_indicator,
            "reason": rel.evidence_reason,
            "investigation_id": src_ent.investigation_id,
        })

    # Find all investigations sharing this exact normalized value
    related_entities = (
        db.query(Entity)
        .filter(Entity.normalized_value == entity.normalized_value)
        .all()
    )
    related_inv_ids = list({e.investigation_id for e in related_entities})
    related_invs = db.query(Investigation).filter(Investigation.id.in_(related_inv_ids)).all()

    # Evidence sources for parent investigation
    evidence_sources = (
        db.query(EvidenceSource)
        .filter(EvidenceSource.investigation_id == entity.investigation_id)
        .all()
    )

    confidence_expl = (
        f"High confidence ({round(max([c['confidence'] for c in connections], default=0.9) * 100)}%) based on "
        f"exact normalized identifier match for '{entity.normalized_value}'."
        if len(connections) > 0
        else "Single-observation node with no cross-case links detected yet."
    )

    return {
        "entity_id": entity.id,
        "type": entity.entity_type,
        "raw_value": entity.raw_value,
        "normalized_value": entity.normalized_value,
        "display_label": entity.display_label,
        "risk_score": entity.risk_score,
        "has_geocoding": entity.has_geocoding,
        "lat": entity.latitude,
        "lng": entity.longitude,
        "country": entity.country,
        "city": entity.city,
        "created_at": entity.created_at,
        "parent_investigation": {
            "id": parent_inv.id if parent_inv else None,
            "case_number": parent_inv.case_number if parent_inv else "N/A",
            "title": parent_inv.title if parent_inv else "Unknown",
            "status": parent_inv.status if parent_inv else "OPEN",
        },
        "related_investigations": [
            {
                "id": inv.id,
                "case_number": inv.case_number,
                "title": inv.title,
                "status": inv.status,
                "risk_score": inv.overall_risk_score,
            }
            for inv in related_invs
        ],
        "connections_count": len(connections),
        "connections": connections,
        "confidence_explanation": confidence_expl,
        "evidence_sources": [
            {
                "id": ev.id,
                "type": ev.source_type,
                "url": ev.source_url,
                "page_title": ev.page_title,
                "retrieved_at": ev.retrieval_timestamp,
                "claims": ev.claims_supported,
            }
            for ev in evidence_sources
        ],
        "recommended_next_actions": [
            f"Trace linked cases for cross-syndicate correlation ({len(related_invs)} cases)",
            f"Check WHOIS / ASN registration for {entity.normalized_value}" if entity.entity_type == "DOMAIN" else "Search entity identifier in threat feeds",
            "Generate formal cyber police report dossier",
        ],
    }
