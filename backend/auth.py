"""
backend/auth.py
All auth + history functions used across the app.

login_user / register_user return dicts with keys:
  {"success": True/False, "message": "...", "user": {...}}

NOTE: login_page.py and register_page.py both use result["message"],
so we use "message" (not "error") as the key.
"""
import re
import sqlite3
import bcrypt
from database.db import get_connection


# ── Validation helpers ────────────────────────────────────────────────────────

def validate_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()))


def password_strength(password: str) -> int:
    """Return score 1-5."""
    score = 0
    if len(password) >= 8:            score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.islower() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password): score += 1
    return max(score, 1)


def validate_password(password: str):
    """Return (ok: bool, message: str)."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    return True, ""


# ── Register ──────────────────────────────────────────────────────────────────

def register_user(username: str, email: str, password: str) -> dict:
    if not username or not email or not password:
        return {"success": False, "message": "All fields are required."}

    if len(username.strip()) < 3:
        return {"success": False, "message": "Username must be at least 3 characters."}

    if not validate_email(email):
        return {"success": False, "message": "Invalid email format."}

    ok, msg = validate_password(password)
    if not ok:
        return {"success": False, "message": msg}

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username.strip(), email.strip().lower(), hashed),
        )
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return {
            "success": True,
            "message": "Account created successfully!",
            "user": {"user_id": user_id, "username": username.strip(), "email": email.strip().lower()},
        }
    except sqlite3.IntegrityError as e:
        err = str(e).lower()
        if "username" in err:
            return {"success": False, "message": "Username already taken."}
        if "email" in err:
            return {"success": False, "message": "Email already registered."}
        return {"success": False, "message": "Registration failed. Please try again."}


# ── Login ─────────────────────────────────────────────────────────────────────

def login_user(identifier: str, password: str) -> dict:
    if not identifier or not password:
        return {"success": False, "message": "Please fill in both fields."}

    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",
        (identifier.strip(), identifier.strip().lower()),
    )
    row = c.fetchone()

    if row:
        # Update last_login
        c.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?", (row["user_id"],))
        conn.commit()
    conn.close()

    if not row:
        return {"success": False, "message": "Invalid credentials. Please check your username/email and password."}

    if not bcrypt.checkpw(password.encode(), row["password"].encode()):
        return {"success": False, "message": "Invalid credentials. Please check your username/email and password."}

    return {
        "success": True,
        "message": "Login successful!",
        "user": {
            "user_id":    row["user_id"],
            "username":   row["username"],
            "email":      row["email"],
            "created_at": row["created_at"],
            "last_login": row["last_login"],
        },
    }


# ── Image history ─────────────────────────────────────────────────────────────

def save_image_history(user_id: int, original_path: str, processed_path: str, style: str):
    """Save a processed image record — field names match image_history table schema."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO image_history
           (user_id, original_image_path, processed_image_path, style_applied)
           VALUES (?, ?, ?, ?)""",
        (user_id, original_path, processed_path, style),
    )
    conn.commit()
    conn.close()


def get_image_history(user_id: int) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM image_history WHERE user_id = ? ORDER BY processing_date DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_password(user_id: int, new_password: str) -> dict:
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    conn = get_connection()
    conn.execute("UPDATE users SET password = ? WHERE user_id = ?", (hashed, user_id))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Password updated."}