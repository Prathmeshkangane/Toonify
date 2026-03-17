import sqlite3
import os

# ── Resolve path relative to THIS file, not the working directory ──────────
# db.py lives at:  cartoonize_app/database/db.py
# DB should be at: cartoonize_app/cartoonize.db  (same folder as app.py)
_HERE   = os.path.dirname(os.path.abspath(__file__))          # .../database/
_ROOT   = os.path.dirname(_HERE)                               # .../cartoonize_app/
DB_PATH = os.path.join(_ROOT, "cartoonize.db")


def get_connection():
    """Primary connection function — also aliased as get_conn."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


get_conn = get_connection   # backward-compat alias


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT    UNIQUE NOT NULL,
            email      TEXT    UNIQUE NOT NULL,
            password   TEXT    NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS image_history (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id              INTEGER NOT NULL,
            original_image_path  TEXT,
            processed_image_path TEXT,
            style_applied        TEXT,
            processing_date      DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # ── Extended Transactions table with full Razorpay fields ──────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS Transactions (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id              INTEGER NOT NULL,
            razorpay_order_id    TEXT    UNIQUE,
            razorpay_payment_id  TEXT,
            razorpay_signature   TEXT,
            amount               INTEGER DEFAULT 10,
            currency             TEXT    DEFAULT 'INR',
            status               TEXT    DEFAULT 'created',
            image_ref            TEXT,
            receipt              TEXT,
            download_count       INTEGER DEFAULT 0,
            created_at           DATETIME DEFAULT CURRENT_TIMESTAMP,
            paid_at              DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # ── Migrate existing Transactions table if columns are missing ──────────
    existing = {row[1] for row in c.execute("PRAGMA table_info(Transactions)").fetchall()}
    migrations = [
        ("razorpay_order_id",   "TEXT UNIQUE"),
        ("razorpay_payment_id", "TEXT"),
        ("razorpay_signature",  "TEXT"),
        ("amount",              "INTEGER DEFAULT 10"),
        ("currency",            "TEXT DEFAULT 'INR'"),
        ("status",              "TEXT DEFAULT 'created'"),
        ("image_ref",           "TEXT"),
        ("receipt",             "TEXT"),
        ("download_count",      "INTEGER DEFAULT 0"),
        ("paid_at",             "DATETIME"),
    ]
    for col, definition in migrations:
        if col not in existing:
            try:
                c.execute(f"ALTER TABLE Transactions ADD COLUMN {col} {definition}")
            except Exception:
                pass

    conn.commit()
    conn.close()