"""
payment/razorpay_handler.py
Razorpay payment integration backend.

Functions:
  create_order(amount_inr, user_id, image_ref)  → dict
  verify_payment(order_id, payment_id, signature) → bool
  save_transaction(...)                           → int  (transaction DB id)
  get_transaction(order_id)                       → dict | None
  get_user_transactions(user_id)                  → list
  mark_downloaded(order_id)                       → None
"""

import hashlib
import hmac
import os
import uuid
import time
import json

# ── Optional Razorpay SDK (graceful fallback for test mode) ──────────────────
try:
    import razorpay as _razorpay_sdk
    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False

from database.db import get_connection

# ── Config ───────────────────────────────────────────────────────────────────
RAZORPAY_KEY_ID     = os.getenv("RAZORPAY_KEY_ID",     "rzp_test_XXXXXXXXXXXXXXXXXX")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "your_test_secret_here")

PRICE_PER_DOWNLOAD_INR = 10   # ₹10 per image download
CURRENCY               = "INR"


def _get_client():
    """Return a Razorpay client if SDK is available."""
    if _SDK_AVAILABLE:
        return _razorpay_sdk.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    return None


# ── Order creation ────────────────────────────────────────────────────────────

def create_order(amount_inr: int, user_id: int, image_ref: str = "") -> dict:
    """
    Create a Razorpay order and persist it to the DB.

    Returns:
        {
            "success": True/False,
            "order_id": "order_...",   # Razorpay order id
            "amount":   1000,          # paise
            "currency": "INR",
            "key_id":   "rzp_test_...",
            "message":  "...",
        }
    """
    amount_paise = amount_inr * 100
    receipt      = f"rcpt_{user_id}_{uuid.uuid4().hex[:8]}"

    razorpay_order_id = None
    client = _get_client()

    if client:
        try:
            order = client.order.create({
                "amount":   amount_paise,
                "currency": CURRENCY,
                "receipt":  receipt,
                "notes":    {"user_id": str(user_id), "image_ref": image_ref},
            })
            razorpay_order_id = order["id"]
        except Exception as e:
            return {"success": False, "message": f"Razorpay API error: {e}"}
    else:
        # Demo / test-mode: generate a fake order id
        razorpay_order_id = f"order_DEMO_{uuid.uuid4().hex[:16].upper()}"

    # Persist to DB
    conn = get_connection()
    conn.execute(
        """INSERT INTO Transactions
           (user_id, razorpay_order_id, amount, currency, status, image_ref, receipt)
           VALUES (?, ?, ?, ?, 'created', ?, ?)""",
        (user_id, razorpay_order_id, amount_inr, CURRENCY, image_ref, receipt),
    )
    conn.commit()
    conn.close()

    return {
        "success":  True,
        "order_id": razorpay_order_id,
        "amount":   amount_paise,
        "currency": CURRENCY,
        "key_id":   RAZORPAY_KEY_ID,
        "message":  "Order created successfully",
    }


# ── Signature verification ────────────────────────────────────────────────────

def verify_payment(razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
    """
    Verify Razorpay payment signature.
    Returns True if valid (or if in demo mode with a demo payment).
    """
    # Demo mode bypass
    if razorpay_order_id.startswith("order_DEMO_") or razorpay_payment_id.startswith("pay_DEMO_"):
        return True

    client = _get_client()
    if client:
        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id":   razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature":  razorpay_signature,
            })
            return True
        except Exception:
            return False

    # Manual HMAC verification fallback
    body    = f"{razorpay_order_id}|{razorpay_payment_id}"
    digest  = hmac.new(RAZORPAY_KEY_SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, razorpay_signature)


# ── DB helpers ────────────────────────────────────────────────────────────────

def save_transaction(
    razorpay_order_id:   str,
    razorpay_payment_id: str,
    razorpay_signature:  str,
    status:              str = "paid",
) -> bool:
    """Update transaction record after payment callback."""
    conn = get_connection()
    conn.execute(
        """UPDATE Transactions
           SET razorpay_payment_id = ?,
               razorpay_signature  = ?,
               status              = ?,
               paid_at             = CURRENT_TIMESTAMP
           WHERE razorpay_order_id = ?""",
        (razorpay_payment_id, razorpay_signature, status, razorpay_order_id),
    )
    conn.commit()
    conn.close()
    return True


def get_transaction(razorpay_order_id: str) -> dict | None:
    conn = get_connection()
    row  = conn.execute(
        "SELECT * FROM Transactions WHERE razorpay_order_id = ?",
        (razorpay_order_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_transactions(user_id: int) -> list:
    conn  = get_connection()
    rows  = conn.execute(
        "SELECT * FROM Transactions WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_downloaded(razorpay_order_id: str):
    conn = get_connection()
    conn.execute(
        "UPDATE Transactions SET download_count = COALESCE(download_count, 0) + 1 WHERE razorpay_order_id = ?",
        (razorpay_order_id,),
    )
    conn.commit()
    conn.close()


def is_payment_verified(razorpay_order_id: str) -> bool:
    """Quick check: is this order paid?"""
    tx = get_transaction(razorpay_order_id)
    return bool(tx and tx.get("status") == "paid")