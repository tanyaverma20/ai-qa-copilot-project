from __future__ import annotations

import sqlite3
from typing import Any


class AuthenticationError(Exception):
    """Raised when login credentials are invalid."""


class ProductNotFoundError(Exception):
    """Raised when a product id does not exist."""


class InsufficientStockError(Exception):
    """Raised when a product does not have enough stock."""


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def authenticate_user(
    connection: sqlite3.Connection,
    username: str,
    password: str,
) -> dict[str, Any]:
    row = connection.execute(
        "SELECT id, username FROM users WHERE username = ? AND password = ?",
        (username, password),
    ).fetchone()
    if row is None:
        raise AuthenticationError("Invalid username or password")
    return _row_to_dict(row)


def token_for_username(username: str) -> str:
    return f"demo-token:{username}"


def username_from_token(token: str) -> str:
    prefix = "demo-token:"
    if not token.startswith(prefix):
        raise AuthenticationError("Invalid token")
    return token.removeprefix(prefix)


def list_products(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT id, name, price_cents, stock FROM products ORDER BY id"
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def get_product(connection: sqlite3.Connection, product_id: int) -> dict[str, Any]:
    row = connection.execute(
        "SELECT id, name, price_cents, stock FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()
    if row is None:
        raise ProductNotFoundError(f"Product {product_id} not found")
    return _row_to_dict(row)


def create_order(
    connection: sqlite3.Connection,
    username: str,
    product_id: int,
    quantity: int,
) -> dict[str, Any]:
    product = get_product(connection, product_id)
    if product["stock"] < quantity:
        raise InsufficientStockError("Not enough stock for requested quantity")

    with connection:
        connection.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (quantity, product_id),
        )
        cursor = connection.execute(
            """
            INSERT INTO orders (username, product_id, quantity, status)
            VALUES (?, ?, ?, ?)
            """,
            (username, product_id, quantity, "created"),
        )

    return {
        "id": cursor.lastrowid,
        "username": username,
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "status": "created",
    }
