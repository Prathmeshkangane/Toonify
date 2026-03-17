
import uuid, json
from datetime import datetime
from database.db import get_connection

try:
    import stripe as _stripe
    _STRIPE_OK = True
except ImportError:
    _STRIPE_OK = False

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG  —  paste your keys from https://dashboard.stripe.com/test/apikeys
# ══════════════════════════════════════════════════════════════════════════════
STRIPE_SECRET_KEY      = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET  = os.getenv("STRIPE_WEBHOOK_SECRET", "")
PRICE_INR              = 1000        # ₹10 in paise
CURRENCY               = "inr"

# ── FREE MODE ─────────────────────────────────────────────────────────────────
# True  = bypass all payments, all downloads are free
# False = real Stripe checkout (add your keys above first)
FREE_MODE = True
# ══════════════════════════════════════════════════════════════════════════════


def _stripe_client():
    if not _STRIPE_OK:
        raise RuntimeError(
            "Stripe SDK not installed.\n"
            "Run:  pip install stripe\n"
            "Then add your API keys to backend/payment.py"
        )
    _stripe.api_key = STRIPE_SECRET_KEY
    return _stripe


def create_payment_intent(user_id: int, image_id: int, amount_paise: int = PRICE_INR) -> dict:
    if FREE_MODE:
        return _free_mode_unlock(user_id, image_id)

    receipt_id = f"rcpt_{user_id}_{image_id}_{uuid.uuid4().hex[:8]}"
    try:
        stripe = _stripe_client()
        intent = stripe.PaymentIntent.create(
            amount=amount_paise,
            currency=CURRENCY,
            payment_method_types=["card"],
            metadata={
                "user_id":    str(user_id),
                "image_id":   str(image_id),
                "receipt_id": receipt_id,
            },
            description=f"CartoonizeMe image download — image #{image_id}",
        )
        conn = get_connection()
        conn.execute("""
            INSERT INTO Transactions
              (user_id, image_id, stripe_payment_intent_id, amount, currency, status, receipt_id)
            VALUES (?,?,?,?,?,?,?)
        """, (user_id, image_id, intent["id"],
              amount_paise / 100, CURRENCY.upper(), "pending", receipt_id))
        conn.commit()
        conn.close()
        return {
            "success":         True,
            "client_secret":   intent["client_secret"],
            "intent_id":       intent["id"],
            "amount":          amount_paise,
            "currency":        CURRENCY,
            "publishable_key": STRIPE_PUBLISHABLE_KEY,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def confirm_payment(payment_intent_id: str) -> dict:
    try:
        stripe = _stripe_client()
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if intent["status"] != "succeeded":
            return {"success": False, "message": f"Payment status: {intent['status']}. Not yet confirmed."}

        now      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        image_id = int(intent["metadata"].get("image_id", 0))
        conn = get_connection()
        conn.execute("""
            UPDATE Transactions SET status='success', updated_at=?
            WHERE stripe_payment_intent_id=?
        """, (now, payment_intent_id))
        if image_id:
            conn.execute("UPDATE image_history SET payment_status='paid' WHERE id=?", (image_id,))
        conn.commit()
        conn.close()
        return {"success": True, "image_id": image_id, "payment_id": payment_intent_id,
                "message": "Payment confirmed! Your image is ready to download."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def verify_payment_by_id(payment_intent_id: str, user_id: int, image_id: int) -> dict:
    if not payment_intent_id.startswith("pi_"):
        return {"success": False, "message": "Invalid Payment Intent ID. It should start with 'pi_'."}
    return confirm_payment(payment_intent_id)


def mark_payment_failed(intent_id: str, reason: str = "failed") -> dict:
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    conn.execute("UPDATE Transactions SET status=?, updated_at=? WHERE stripe_payment_intent_id=?",
                 (reason, now, intent_id))
    conn.commit()
    conn.close()
    return {"success": False, "message": f"Payment {reason}."}


def handle_webhook(payload: str, sig_header: str) -> dict:
    if not STRIPE_WEBHOOK_SECRET:
        return {"success": False, "message": "Webhook secret not configured."}
    try:
        stripe = _stripe_client()
        event  = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        if event["type"] == "payment_intent.succeeded":
            intent   = event["data"]["object"]
            image_id = int(intent["metadata"].get("image_id", 0))
            conn     = get_connection()
            conn.execute("UPDATE Transactions SET status='success' WHERE stripe_payment_intent_id=?",
                         (intent["id"],))
            if image_id:
                conn.execute("UPDATE image_history SET payment_status='paid' WHERE id=?", (image_id,))
            conn.commit()
            conn.close()
        return {"success": True, "event": event["type"]}
    except Exception as e:
        return {"success": False, "message": str(e)}


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
        """, (user_id, image_id, f"pi_FREE_{image_id}", 0.0, "INR", "success", f"free_{image_id}"))
        conn.commit()
    conn.close()
    return {"success": True, "free_mode": True, "image_id": image_id}


def get_transaction_by_image(image_id: int) -> dict | None:
    conn = get_connection()
    row  = conn.execute(
        "SELECT * FROM Transactions WHERE image_id=? ORDER BY created_at DESC LIMIT 1", (image_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_transactions(user_id: int) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.*, ih.style_applied, ih.download_format
        FROM   Transactions t
        LEFT JOIN image_history ih ON ih.id = t.image_id
        WHERE  t.user_id=? ORDER BY t.created_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]