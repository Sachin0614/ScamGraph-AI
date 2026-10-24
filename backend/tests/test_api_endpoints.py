"""
ScamGraph AI - API Endpoints Integration Test Suite
Tests FastAPI router integrations with TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.session import get_db
from app.models.investigation import Base, Investigation, InvestigationStatus, Entity, EntityType, Relationship, RelationshipType
from app.database.seed_data import seed_sample_investigations


from sqlalchemy.pool import StaticPool

@pytest.fixture(scope="function")
def client_with_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Seed sample data into in-memory db
    with TestingSessionLocal() as s:
        seed_sample_investigations(s)

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_health_and_root(client_with_db):
    res = client_with_db.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    res_api = client_with_db.get("/api")
    assert res_api.status_code == 200
    assert "ScamGraph" in res_api.json()["service"]

    # Verify frontend index is served at /
    res_root = client_with_db.get("/")
    assert res_root.status_code == 200
    assert "<!doctype html>" in res_root.text.lower()


def test_dashboard_stats(client_with_db):
    res = client_with_db.get("/api/v1/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert data["metrics"]["total_investigations"] >= 4
    assert data["metrics"]["total_entities"] > 0
    assert len(data["recent_activity"]) > 0


def test_list_investigations(client_with_db):
    res = client_with_db.get("/api/v1/investigations")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 4
    assert any("TCS" in item["title"] for item in items)


def test_create_and_delete_investigation(client_with_db):
    payload = {
        "title": "Suspected Amazon Data Entry Scam",
        "raw_text": "Earn Rs 5000 daily from home doing Amazon product rating. Pay Rs 1500 registration deposit via UPI: amazonpay@icici.",
        "website_url": "https://amazon-careers-verify.online",
        "recruiter_name": "Priya Sharma",
        "email": "priya.amazon.hr@gmail.com",
        "phone": "+91 99887 76655",
        "payment_id": "amazonpay@icici",
        "notes": "Victim received WhatsApp message.",
    }
    res = client_with_db.post("/api/v1/investigations", json=payload)
    assert res.status_code == 201
    created = res.json()
    assert created["id"] is not None
    assert created["overall_risk_score"] >= 65.0
    assert len(created["entities"]) >= 5
    assert len(created["indicators"]) >= 2
    assert len(created["events"]) >= 5

    # Test detail fetch
    detail_res = client_with_db.get(f"/api/v1/investigations/{created['id']}")
    assert detail_res.status_code == 200
    assert detail_res.json()["case_number"] == created["case_number"]

    # Test delete
    del_res = client_with_db.delete(f"/api/v1/investigations/{created['id']}")
    assert del_res.status_code == 204

    # Verify 404 after deletion
    after_del = client_with_db.get(f"/api/v1/investigations/{created['id']}")
    assert after_del.status_code == 404


def test_graph_endpoints(client_with_db):
    # Fetch full graph
    res = client_with_db.get("/api/v1/graph")
    assert res.status_code == 200
    graph = res.json()
    assert len(graph["nodes"]) > 0
    assert len(graph["edges"]) > 0
    assert "stats" in graph

    first_node = graph["nodes"][0]
    entity_id = first_node["numeric_id"]

    # Entity inspection details (Section 9)
    detail_res = client_with_db.get(f"/api/v1/graph/entity/{entity_id}/details")
    assert detail_res.status_code == 200
    details = detail_res.json()
    assert "entity_id" in details
    assert "connections" in details
    assert "confidence_explanation" in details

    # Cluster expansion
    cluster_res = client_with_db.get(f"/api/v1/graph/cluster/{entity_id}?radius=1")
    assert cluster_res.status_code == 200
    assert "nodes" in cluster_res.json()


def test_safety_assistant_api(client_with_db):
    payload = {
        "has_paid": True,
        "shared_otp": True,
        "amount_lost": 12000.0,
        "payment_reference": "UPI/402847291048",
    }
    res = client_with_db.post("/api/v1/safety/assess", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["actions"]) >= 3
    assert any("1930" in a["title"] or "1930" in a.get("helpline", "") for a in data["actions"])

    portals_res = client_with_db.get("/api/v1/safety/portals")
    assert portals_res.status_code == 200
    assert len(portals_res.json()["portals"]) >= 4


def test_settings_api(client_with_db):
    res = client_with_db.get("/api/v1/settings")
    assert res.status_code == 200
    settings_data = res.json()
    assert "tinyfish_enabled" in settings_data

    # Test update
    update_res = client_with_db.post("/api/v1/settings", json={"tinyfish_enabled": False})
    assert update_res.status_code == 200
