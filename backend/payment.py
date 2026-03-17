from datetime import datetime
from database.db import get_connection

# FREE MODE ONLY — no Stripe at all

def create_payment_intent(user_id: int, image_id: int) -> dict:
    return _free_mode_unlock(user_id, image_id)


def confirm_payment(payment_intent_id: str) -> dict:
    return {"success": True, "message": "Free mode active"}


def _free_mode_unlock(user_id: int, image_id: int) -> dict:
    from backend.download_manager import mark_image_paid

    mark_image_paid(image_id)

    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM Transactions WHERE image_id=? AND user_id=? AND status='success'",
        (image_id, user_id)
    ).fetchone()

    if not existing:
        conn.execute("""
            INSERT INTO Transactions
              (user_id, image_id, stripe_payment_intent_id, amount, currency, status, receipt_id)
            VALUES (?,?,?,?,?,?,?)
        """, (user_id, image_id, f"FREE_{image_id}", 0.0, "INR", "success", f"free_{image_id}"))

        conn.commit()

    conn.close()

    return {"success": True, "free_mode": True, "image_id": image_id}