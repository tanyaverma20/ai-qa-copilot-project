from __future__ import annotations


def test_list_products(client):
    response = client.get("/api/products")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "无线鼠标"


def test_get_product_by_id(client):
    response = client.get("/api/products/1")

    assert response.status_code == 200
    assert response.json()["stock"] == 10


def test_get_product_returns_404_for_missing_id(client):
    response = client.get("/api/products/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product 999 not found"
