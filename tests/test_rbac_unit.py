from fastapi.testclient import TestClient
from rag_app import app


def test_health_endpoint():
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"


def test_engineer_can_read_runbook():
    with TestClient(app) as client:
        res = client.post(
            "/query",
            headers={"X-User-Role": "engineering"},
            json={"question": "What is the procedure for a SEV-1 outage?"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "answered"
        assert "PagerDuty" in data["answer"]
        assert data["latency_ms"] >= 0
        assert data["estimated_cost_usd"] >= 0
        assert any(c["doc_id"] == "DOC-ENG-01" for c in data["citations"])


def test_engineer_blocked_from_hr_salaries():
    with TestClient(app) as client:
        res = client.post(
            "/query",
            headers={"X-User-Role": "engineering"},
            json={"question": "What is the L5 Senior Engineer base salary band?"},
        )
        assert res.status_code == 200
        data = res.json()
        assert "$175,000" not in data["answer"]
        assert "DOC-HR-01" not in [c["doc_id"] for c in data["citations"]]


def test_invalid_role_returns_403():
    with TestClient(app) as client:
        res = client.post(
            "/query",
            headers={"X-User-Role": "superadmin"},
            json={"question": "Show me everything"},
        )
        assert res.status_code == 403
