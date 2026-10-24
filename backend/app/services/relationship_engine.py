"""
ScamGraph AI - Relationship Detection and Graph Engine
Correlates new investigations against historical cases using normalized digital indicators.
Builds and queries the relationship graph using NetworkX.
Calculates shortest relationship paths, detects connected scam syndicates, and prepares 3D globe/graph payloads.
"""

import math
import json
import networkx as nx
from typing import List, Dict, Any, Optional, Tuple, Set
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.investigation import (
    Entity,
    EntityType,
    Relationship,
    RelationshipType,
    Investigation,
    EvidenceSource,
)
from app.services.normalizer import normalizer


class RelationshipEngine:
    """
    Engine for cross-investigation entity linking and topological graph analysis.
    """

    RELATIONSHIP_CONFIDENCE = {
        RelationshipType.SAME_PAYMENT_ID.value: 0.98,
        RelationshipType.SAME_EMAIL.value: 0.95,
        RelationshipType.SAME_DOMAIN.value: 0.95,
        RelationshipType.SAME_PHONE.value: 0.90,
        RelationshipType.SHARED_RECRUITER.value: 0.70,
        RelationshipType.SIMILAR_CONTENT.value: 0.60,
    }

    def correlate_investigation(
        self,
        db: Session,
        current_investigation_id: int,
        entities_created: List[Entity],
        offer_text: Optional[str] = None,
    ) -> List[Relationship]:
        """
        Scans all entities in current_investigation against past entities in the database.
        Creates explicit Relationship records when an evidence-supported match is verified.
        """
        new_relationships = []

        for entity in entities_created:
            # Query existing entities of matching type and normalized_value across OTHER investigations
            matching_entities = (
                db.query(Entity)
                .filter(
                    Entity.investigation_id != current_investigation_id,
                    Entity.entity_type == entity.entity_type,
                    Entity.normalized_value == entity.normalized_value,
                )
                .all()
            )

            for target_ent in matching_entities:
                # Determine relationship type
                rel_type = RelationshipType.OTHER.value
                reason = ""
                confidence = 0.85

                if entity.entity_type == EntityType.DOMAIN.value:
                    rel_type = RelationshipType.SAME_DOMAIN.value
                    confidence = self.RELATIONSHIP_CONFIDENCE[rel_type]
                    reason = f"Both investigations share identical registered domain target: '{entity.normalized_value}'"
                elif entity.entity_type == EntityType.EMAIL.value:
                    rel_type = RelationshipType.SAME_EMAIL.value
                    confidence = self.RELATIONSHIP_CONFIDENCE[rel_type]
                    reason = f"Both investigations document communications from identical email address: '{entity.normalized_value}'"
                elif entity.entity_type == EntityType.PHONE.value:
                    rel_type = RelationshipType.SAME_PHONE.value
                    confidence = self.RELATIONSHIP_CONFIDENCE[rel_type]
                    reason = f"Both investigations trace contact to identical telephone identifier: '{entity.normalized_value}'"
                elif entity.entity_type == EntityType.PAYMENT_ID.value:
                    rel_type = RelationshipType.SAME_PAYMENT_ID.value
                    confidence = self.RELATIONSHIP_CONFIDENCE[rel_type]
                    reason = f"Critical link: identical financial payment account / UPI ID used across cases: '{entity.normalized_value}'"
                elif entity.entity_type == EntityType.RECRUITER.value:
                    rel_type = RelationshipType.SHARED_RECRUITER.value
                    confidence = self.RELATIONSHIP_CONFIDENCE[rel_type]
                    reason = f"Same recruiter persona or pseudonymous handle claimed: '{entity.normalized_value}'"

                # Check if relationship already exists
                existing_rel = (
                    db.query(Relationship)
                    .filter(
                        or_(
                            (Relationship.source_entity_id == entity.id) & (Relationship.target_entity_id == target_ent.id),
                            (Relationship.source_entity_id == target_ent.id) & (Relationship.target_entity_id == entity.id),
                        )
                    )
                    .first()
                )

                if not existing_rel:
                    rel = Relationship(
                        source_entity_id=entity.id,
                        target_entity_id=target_ent.id,
                        relationship_type=rel_type,
                        confidence=confidence,
                        matching_indicator=entity.normalized_value,
                        evidence_reason=reason,
                    )
                    db.add(rel)
                    new_relationships.append(rel)

        # Content similarity check between job offers
        if offer_text and len(offer_text) > 30:
            current_tokens = set(offer_text.lower().split())
            # Find past JOB_OFFER entities
            past_job_entities = (
                db.query(Entity)
                .filter(
                    Entity.investigation_id != current_investigation_id,
                    Entity.entity_type == EntityType.JOB_OFFER.value,
                )
                .all()
            )

            current_job_node = next(
                (e for e in entities_created if e.entity_type == EntityType.JOB_OFFER.value), None
            )

            if current_job_node:
                for past_job in past_job_entities:
                    if not past_job.raw_value:
                        continue
                    past_tokens = set(past_job.raw_value.lower().split())
                    if not past_tokens:
                        continue
                    # Jaccard index
                    intersection = current_tokens.intersection(past_tokens)
                    union = current_tokens.union(past_tokens)
                    similarity = len(intersection) / len(union) if union else 0.0

                    if similarity >= 0.45:  # Significant textual phrasing match
                        existing_rel = (
                            db.query(Relationship)
                            .filter(
                                or_(
                                    (Relationship.source_entity_id == current_job_node.id) & (Relationship.target_entity_id == past_job.id),
                                    (Relationship.source_entity_id == past_job.id) & (Relationship.target_entity_id == current_job_node.id),
                                )
                            )
                            .first()
                        )
                        if not existing_rel:
                            rel = Relationship(
                                source_entity_id=current_job_node.id,
                                target_entity_id=past_job.id,
                                relationship_type=RelationshipType.SIMILAR_CONTENT.value,
                                confidence=round(0.50 + (similarity * 0.4), 2),
                                matching_indicator=f"Text similarity {round(similarity * 100)}%",
                                evidence_reason=f"Significant textual pattern match ({round(similarity * 100)}% vocabulary overlap) indicating shared scam playbook or template.",
                            )
                            db.add(rel)
                            new_relationships.append(rel)

        db.flush()
        return new_relationships

    def build_networkx_graph(self, db: Session) -> nx.Graph:
        """Constructs a NetworkX graph from database entities and relationships."""
        G = nx.Graph()

        entities = db.query(Entity).all()
        for e in entities:
            G.add_node(
                e.id,
                label=e.display_label,
                type=e.entity_type,
                value=e.normalized_value,
                investigation_id=e.investigation_id,
                risk=e.risk_score,
            )

        relationships = db.query(Relationship).all()
        for r in relationships:
            G.add_edge(
                r.source_entity_id,
                r.target_entity_id,
                id=r.id,
                type=r.relationship_type,
                confidence=r.confidence,
                indicator=r.matching_indicator,
                reason=r.evidence_reason,
            )

        return G

    def get_full_graph_data(
        self,
        db: Session,
        entity_types: Optional[List[str]] = None,
        min_confidence: float = 0.0,
        investigation_id: Optional[int] = None,
        search_query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Exports graph data with nodes, edges, statistics, clusters, and 3D positioning.
        """
        entity_query = db.query(Entity)
        if entity_types:
            entity_query = entity_query.filter(Entity.entity_type.in_(entity_types))
        if investigation_id:
            entity_query = entity_query.filter(Entity.investigation_id == investigation_id)

        all_entities = entity_query.all()
        entity_id_map = {e.id: e for e in all_entities}

        rel_query = db.query(Relationship).filter(Relationship.confidence >= min_confidence)
        all_relationships = rel_query.all()

        # Filter relationships where both nodes exist in the entity map or add missing connected nodes
        valid_node_ids = set(entity_id_map.keys())

        # If a search query is provided, find matching nodes and their 1-hop neighbors
        if search_query:
            sq = search_query.strip().lower()
            matching_ids = {
                e.id for e in all_entities
                if sq in e.display_label.lower()
                or sq in e.normalized_value.lower()
                or sq in str(e.investigation_id)
            }
            # Expand to 1-hop connected neighbors
            expanded_ids = set(matching_ids)
            for r in all_relationships:
                if r.source_entity_id in matching_ids:
                    expanded_ids.add(r.target_entity_id)
                elif r.target_entity_id in matching_ids:
                    expanded_ids.add(r.source_entity_id)
            valid_node_ids = expanded_ids

        nodes_list = []
        node_id_set = set()

        # Layout generation: spherical/fibonacci spiral for 3D globe presentation
        total_nodes = max(len(valid_node_ids), 1)
        golden_angle = math.pi * (3 - math.sqrt(5))

        for idx, (node_id, ent) in enumerate(entity_id_map.items()):
            if node_id not in valid_node_ids:
                continue

            # Fibonacci sphere projection for globe coordinates
            y = 1 - (idx / float(total_nodes - 1 or 1)) * 2  # y from 1 to -1
            radius_at_y = math.sqrt(max(0.0, 1 - y * y))
            theta = golden_angle * idx
            x = math.cos(theta) * radius_at_y
            z = math.sin(theta) * radius_at_y

            globe_radius = 120.0
            pos_x = round(x * globe_radius, 2)
            pos_y = round(y * globe_radius, 2)
            pos_z = round(z * globe_radius, 2)

            # Node color by type
            color_map = {
                EntityType.JOB_OFFER.value: "#00F0FF",      # Electric Cyan
                EntityType.DOMAIN.value: "#A855F7",         # Violet
                EntityType.EMAIL.value: "#F59E0B",          # Amber/Gold
                EntityType.PHONE.value: "#10B981",          # Emerald
                EntityType.PAYMENT_ID.value: "#EF4444",     # Red Alert
                EntityType.RECRUITER.value: "#EC4899",      # Pink
                EntityType.ORGANIZATION.value: "#3B82F6",   # Blue
                EntityType.TELEGRAM.value: "#06B6D4",       # Teal
                EntityType.WHATSAPP.value: "#22C55E",       # Green
            }

            nodes_list.append({
                "id": str(ent.id),
                "numeric_id": ent.id,
                "label": ent.display_label,
                "type": ent.entity_type,
                "value": ent.normalized_value,
                "raw_value": ent.raw_value,
                "investigation_id": ent.investigation_id,
                "risk_score": ent.risk_score,
                "color": color_map.get(ent.entity_type, "#94A3B8"),
                "has_geocoding": ent.has_geocoding,
                "lat": ent.latitude,
                "lng": ent.longitude,
                "x": pos_x,
                "y": pos_y,
                "z": pos_z,
            })
            node_id_set.add(ent.id)

        edges_list = []
        for r in all_relationships:
            if r.source_entity_id in node_id_set and r.target_entity_id in node_id_set:
                edges_list.append({
                    "id": f"e_{r.id}",
                    "source": str(r.source_entity_id),
                    "target": str(r.target_entity_id),
                    "relationship_type": r.relationship_type,
                    "confidence": r.confidence,
                    "matching_indicator": r.matching_indicator,
                    "evidence_reason": r.evidence_reason,
                    "color": "#EF4444" if r.confidence >= 0.9 else ("#A855F7" if r.confidence >= 0.7 else "#00F0FF"),
                })

        # Calculate graph statistics
        G = nx.Graph()
        for n in nodes_list:
            G.add_node(n["id"])
        for e in edges_list:
            G.add_edge(e["source"], e["target"])

        connected_components_count = nx.number_connected_components(G) if len(G) > 0 else 0
        density = nx.density(G) if len(G) > 0 else 0.0

        return {
            "nodes": nodes_list,
            "edges": edges_list,
            "stats": {
                "total_nodes": len(nodes_list),
                "total_edges": len(edges_list),
                "connected_clusters": connected_components_count,
                "network_density": round(density, 4),
            },
        }

    def find_shortest_path(self, db: Session, start_entity_id: int, end_entity_id: int) -> Dict[str, Any]:
        """
        Finds the shortest evidence-backed chain linking two entities.
        """
        G = self.build_networkx_graph(db)

        if not G.has_node(start_entity_id) or not G.has_node(end_entity_id):
            return {
                "found": False,
                "message": "One or both entities not found in graph.",
                "path": [],
            }

        try:
            path_node_ids = nx.shortest_path(G, source=start_entity_id, target=end_entity_id)
            path_details = []
            for nid in path_node_ids:
                ent = db.query(Entity).filter(Entity.id == nid).first()
                if ent:
                    path_details.append({
                        "id": ent.id,
                        "label": ent.display_label,
                        "type": ent.entity_type,
                        "value": ent.normalized_value,
                        "investigation_id": ent.investigation_id,
                    })

            # Get edge details along path
            path_edges = []
            for i in range(len(path_node_ids) - 1):
                u, v = path_node_ids[i], path_node_ids[i + 1]
                edge_data = G.get_edge_data(u, v)
                path_edges.append(edge_data)

            return {
                "found": True,
                "length": len(path_node_ids) - 1,
                "path_nodes": path_details,
                "path_edges": path_edges,
            }
        except nx.NetworkXNoPath:
            return {
                "found": False,
                "message": "No connected relationship path exists between the selected entities.",
                "path_nodes": [],
                "path_edges": [],
            }

    def expand_cluster(self, db: Session, entity_id: int, radius: int = 1) -> Dict[str, Any]:
        """Returns the ego-graph (neighborhood) centered around a specific entity."""
        G = self.build_networkx_graph(db)
        if not G.has_node(entity_id):
            return {"nodes": [], "edges": []}

        subgraph = nx.ego_graph(G, n=entity_id, radius=radius)
        subgraph_nodes = list(subgraph.nodes())

        entities = db.query(Entity).filter(Entity.id.in_(subgraph_nodes)).all()
        relationships = (
            db.query(Relationship)
            .filter(
                Relationship.source_entity_id.in_(subgraph_nodes),
                Relationship.target_entity_id.in_(subgraph_nodes),
            )
            .all()
        )

        return {
            "center_id": entity_id,
            "radius": radius,
            "node_count": len(entities),
            "edge_count": len(relationships),
            "nodes": [
                {
                    "id": str(e.id),
                    "label": e.display_label,
                    "type": e.entity_type,
                    "value": e.normalized_value,
                    "investigation_id": e.investigation_id,
                }
                for e in entities
            ],
            "edges": [
                {
                    "source": str(r.source_entity_id),
                    "target": str(r.target_entity_id),
                    "relationship_type": r.relationship_type,
                    "confidence": r.confidence,
                    "reason": r.evidence_reason,
                }
                for r in relationships
            ],
        }


relationship_engine = RelationshipEngine()
