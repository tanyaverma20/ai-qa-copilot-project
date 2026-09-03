from __future__ import annotations


def test_generate_diagnosis_from_failure_context(client, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post(
        "/api/diagnosis",
        json={
            "nodeid": "tests/api/test_orders_api.py::test_create_order",
            "failed_at": "2026-07-02T10:00:00+00:00",
            "phase": "call",
            "duration_seconds": 0.12,
            "longrepr": "AssertionError: expected 409 but got 500",
            "keywords": ["api", "orders"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["artifact_count"] == 1
    assert "API key is not configured" in payload["report_markdown"]


def test_generate_diagnosis_validates_required_context(client):
    response = client.post("/api/diagnosis", json={"nodeid": "missing fields"})

    assert response.status_code == 422
