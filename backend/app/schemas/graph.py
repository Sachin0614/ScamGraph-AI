"""
ScamGraph AI - Pydantic Schemas for Network Graph and 3D Visualizer
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    id: str
    numeric_id: int
    label: str
    type: str
    value: str
    raw_value: Optional[str] = None
    investigation_id: int
    risk_score: float
    color: str
    has_geocoding: bool = False
    lat: Optional[float] = None
    lng: Optional[float] = None
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relationship_type: str
    confidence: float
    matching_indicator: str
    evidence_reason: str
    color: str


class GraphStats(BaseModel):
    total_nodes: int
    total_edges: int
    connected_clusters: int
    network_density: float


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    stats: GraphStats


class ShortestPathRequest(BaseModel):
    start_entity_id: int
    end_entity_id: int


class ShortestPathResponse(BaseModel):
    found: bool
    length: Optional[int] = 0
    message: Optional[str] = None
    path_nodes: List[Dict[str, Any]] = []
    path_edges: List[Dict[str, Any]] = []


class ClusterExpandResponse(BaseModel):
    center_id: int
    radius: int
    node_count: int
    edge_count: int
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
