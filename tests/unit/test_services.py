from __future__ import annotations

import pytest

from app.db import connect, initialize_database, seed_database
from app.services import (
    AuthenticationError,
    InsufficientStockError,
    ProductNotFoundError,
    authenticate_user,
    create_order,
    list_products,
)


@pytest.fixture()
def db():
    connection = connect(":memory:")
    initialize_database(connection)
    seed_database(connection)
    yield connection
    connection.close()


def test_authenticate_user_accepts_known_user(db):
    user = authenticate_user(db, "alice", "password123")

    assert user["username"] == "alice"


def test_authenticate_user_rejects_bad_password(db):
    with pytest.raises(AuthenticationError):
        authenticate_user(db, "alice", "wrong-password")


def test_list_products_returns_seeded_catalog(db):
    products = list_products(db)

    assert [product["name"] for product in products] == [
        "无线鼠标",
        "机械键盘",
        "USB-C 扩展坞",
    ]


def test_create_order_reduces_stock(db):
    order = create_order(db, username="alice", product_id=1, quantity=2)

    assert order["status"] == "created"
    assert order["quantity"] == 2
    products = list_products(db)
    assert products[0]["stock"] == 8


def test_create_order_rejects_missing_product(db):
    with pytest.raises(ProductNotFoundError):
        create_order(db, username="alice", product_id=999, quantity=1)


def test_create_order_rejects_insufficient_stock(db):
    with pytest.raises(InsufficientStockError):
        create_order(db, username="alice", product_id=1, quantity=99)
