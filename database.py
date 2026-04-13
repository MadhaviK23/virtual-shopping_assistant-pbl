from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "shopping.db"
FACES_DIR = BASE_DIR / "faces"

SEED_PRODUCTS: tuple[tuple[str, float, str], ...] = (
    ("Bottle", 30.0, "Drinks"),
    ("Water", 20.0, "Drinks"),
    ("Chips", 25.0, "Snacks"),
    ("Cake", 60.0, "Bakery"),
    ("Soap", 35.0, "Personal Care"),
    ("Shirt", 799.0, "Fashion"),
)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    FACES_DIR.mkdir(exist_ok=True)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                face_image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                price REAL NOT NULL,
                category TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cart_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
            """
        )
        cursor.executemany(
            """
            INSERT OR IGNORE INTO products (name, price, category)
            VALUES (?, ?, ?)
            """,
            SEED_PRODUCTS,
        )
        conn.commit()


def list_products() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, name, price, category FROM products ORDER BY category, name"
        ).fetchall()


def list_customers() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, name, face_image_path FROM customers ORDER BY name"
        ).fetchall()


def create_customer(name: str, face_image_path: str | None = None) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO customers (name, face_image_path) VALUES (?, ?)",
            (name.strip(), face_image_path),
        )
        conn.commit()
        return int(cursor.lastrowid)


def update_customer_face_path(customer_id: int, face_image_path: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE customers SET face_image_path = ? WHERE id = ?",
            (face_image_path, customer_id),
        )
        conn.commit()


def start_session(customer_id: int) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO sessions (customer_id) VALUES (?)",
            (customer_id,),
        )
        conn.commit()
        return int(cursor.lastrowid)


def add_item_to_cart(session_id: int, product_id: int, quantity: int = 1) -> None:
    with get_connection() as conn:
        existing = conn.execute(
            """
            SELECT id, quantity FROM cart_items
            WHERE session_id = ? AND product_id = ?
            """,
            (session_id, product_id),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE cart_items SET quantity = quantity + ? WHERE id = ?",
                (quantity, existing["id"]),
            )
        else:
            conn.execute(
                """
                INSERT INTO cart_items (session_id, product_id, quantity)
                VALUES (?, ?, ?)
                """,
                (session_id, product_id, quantity),
            )
        conn.commit()


def get_cart_items(session_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT
                cart_items.id,
                products.name,
                products.price,
                products.category,
                cart_items.quantity,
                products.price * cart_items.quantity AS line_total
            FROM cart_items
            JOIN products ON products.id = cart_items.product_id
            WHERE cart_items.session_id = ?
            ORDER BY cart_items.id DESC
            """,
            (session_id,),
        ).fetchall()


def get_cart_total(session_id: int) -> float:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(SUM(products.price * cart_items.quantity), 0)
            FROM cart_items
            JOIN products ON products.id = cart_items.product_id
            WHERE cart_items.session_id = ?
            """,
            (session_id,),
        ).fetchone()
        return float(row[0] or 0)


def checkout_session(session_id: int) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE sessions SET status = 'paid' WHERE id = ?",
            (session_id,),
        )
        conn.commit()


def get_customer(customer_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, name, face_image_path FROM customers WHERE id = ?",
            (customer_id,),
        ).fetchone()
