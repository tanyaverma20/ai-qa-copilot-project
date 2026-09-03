from __future__ import annotations


def test_create_order_with_token(client):
    login = client.post(
        "/api/login",
        json={"username": "alice", "password": "password123"},
    )
    token = login.json()["access_token"]

    response = client.post(
        "/api/orders",
        json={"product_id": 1, "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json()["status"] == "created"


def test_create_order_rejects_missing_auth(client):
    response = client.post("/api/orders", json={"product_id": 1, "quantity": 1})

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing bearer token"


def test_create_order_rejects_insufficient_stock(client):
    login = client.post(
        "/api/login",
        json={"username": "alice", "password": "password123"},
    )
    token = login.json()["access_token"]

    response = client.post(
        "/api/orders",
        json={"product_id": 1, "quantity": 99},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Not enough stock for requested quantity"
