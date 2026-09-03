from __future__ import annotations


def test_login_returns_demo_token(client):
    response = client.post(
        "/api/login",
        json={"username": "alice", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "demo-token:alice"


def test_login_rejects_bad_password(client):
    response = client.post(
        "/api/login",
        json={"username": "alice", "password": "bad-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"
