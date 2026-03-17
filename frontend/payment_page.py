"""
frontend/payment_page.py
Full Razorpay payment flow:
  show_payment_page()      – checkout + Razorpay widget
  show_payment_success()   – confirmation + download
  show_payment_failure()   – error + retry
  show_payment_history()   – all user transactions
"""

import streamlit as st
import streamlit.components.v1 as components
import sys, os, io, uuid, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PIL import Image
from utils.styles import back_button

try:
    from payment.razorpay_handler import (
        create_order, verify_payment, save_transaction,
        get_transaction, get_user_transactions, mark_downloaded,
        is_payment_verified, RAZORPAY_KEY_ID, PRICE_PER_DOWNLOAD_INR,
    )
except ImportError as e:
    st.error(f"Payment module not found: {e}")
    st.stop()


# ── Shared label helper ───────────────────────────────────────────────────────
def _label(text):
    st.markdown(
        f'<p style="font-family:Syne Mono,monospace;font-size:.58rem;color:#3E3C58;'
        f'text-transform:uppercase;letter-spacing:.18em;margin:0 0 10px;">{text}</p>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CHECKOUT PAGE
# ═══════════════════════════════════════════════════════════════════════════════

def show_payment_page():
    back_button("Back to Studio", "image_processing")
    user = st.session_state.get("user", {})

    # Guard – must have a processed image
    if "proc_path" not in st.session_state:
        st.warning("No processed image found. Please create one in Art Studio first.")
        if st.button("Go to Art Studio", type="primary"):
            st.session_state["page"] = "image_processing"
            st.rerun()
        return

    result_style   = st.session_state.get("result_style", "Unknown Effect")
    proc_path      = st.session_state.get("proc_path", "")
    orig_path      = st.session_state.get("orig_path", "")
    result_elapsed = st.session_state.get("result_elapsed", 0)

    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="margin-bottom:28px;">
      <p style="font-family:'Syne Mono',monospace;font-size:.58rem;color:#3E3C58;
                text-transform:uppercase;letter-spacing:.18em;margin:0 0 8px;">Checkout</p>
      <h2 style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
                 color:#EEEAF8;margin:0;letter-spacing:-.04em;">Download Your Artwork</h2>
    </div>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 1.4])

    # ── LEFT – image preview & order summary ─────────────────────────────────
    with left_col:
        _label("Your Artwork")

        if proc_path and os.path.exists(proc_path):
            st.image(proc_path, use_container_width=True)
        else:
            st.markdown("""
            <div style="aspect-ratio:1;border-radius:14px;background:#171723;
                        border:1px solid rgba(255,255,255,.06);display:flex;
                        align-items:center;justify-content:center;font-size:2.5rem;">🖼️</div>
            """, unsafe_allow_html=True)

        # Order summary card
        style_short = result_style.split(" ", 1)[-1] if " " in result_style else result_style
        st.markdown(f"""
        <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.07);
                    border-radius:14px;padding:16px;margin-top:14px;">
          <p style="font-family:'Syne Mono',monospace;font-size:.56rem;color:#3E3C58;
                    text-transform:uppercase;letter-spacing:.12em;margin:0 0 12px;">Order Summary</p>
          {"".join([
              f'<div style="display:flex;justify-content:space-between;align-items:center;'
              f'padding:8px 0;border-bottom:1px solid rgba(255,255,255,.04);">'
              f'<span style="font-family:Outfit,sans-serif;font-size:.82rem;color:#7C7A9A;">{lbl}</span>'
              f'<span style="font-family:Syne Mono,monospace;font-size:.78rem;color:#EEEAF8;">{val}</span></div>'
              for lbl, val in [
                  ("Effect", style_short),
                  ("Format", "PNG (Full Quality)"),
                  ("Processing", f"{result_elapsed}s"),
                  ("Includes", "Comparison Image"),
              ]
          ])}
          <div style="display:flex;justify-content:space-between;align-items:center;
                      padding:12px 0 0;">
            <span style="font-family:'Syne',sans-serif;font-weight:700;
                         font-size:.9rem;color:#EEEAF8;">Total</span>
            <span style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.3rem;
                         background:linear-gradient(135deg,#A78BFA,#F472B6);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                         background-clip:text;">₹{PRICE_PER_DOWNLOAD_INR}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── RIGHT – payment section ───────────────────────────────────────────────
    with right_col:
        _label("Secure Payment")

        # Trust badges
        st.markdown("""
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px;">
          <div style="display:flex;align-items:center;gap:6px;background:rgba(52,211,153,.06);
                      border:1px solid rgba(52,211,153,.15);border-radius:99px;padding:5px 12px;">
            <span style="color:#34D399;font-size:.7rem;">🔒</span>
            <span style="font-family:Syne Mono,monospace;font-size:.56rem;color:#34D399;
                         letter-spacing:.06em;text-transform:uppercase;">SSL Secured</span>
          </div>
          <div style="display:flex;align-items:center;gap:6px;background:rgba(167,139,250,.06);
                      border:1px solid rgba(167,139,250,.15);border-radius:99px;padding:5px 12px;">
            <span style="color:#A78BFA;font-size:.7rem;">⚡</span>
            <span style="font-family:Syne Mono,monospace;font-size:.56rem;color:#A78BFA;
                         letter-spacing:.06em;text-transform:uppercase;">Instant Download</span>
          </div>
          <div style="display:flex;align-items:center;gap:6px;background:rgba(96,165,250,.06);
                      border:1px solid rgba(96,165,250,.15);border-radius:99px;padding:5px 12px;">
            <span style="color:#60A5FA;font-size:.7rem;">✓</span>
            <span style="font-family:Syne Mono,monospace;font-size:.56rem;color:#60A5FA;
                         letter-spacing:.06em;text-transform:uppercase;">Razorpay</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # What you get
        st.markdown(f"""
        <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.07);
                    border-radius:14px;padding:18px;margin-bottom:18px;">
          <p style="font-family:'Syne Mono',monospace;font-size:.56rem;color:#3E3C58;
                    text-transform:uppercase;letter-spacing:.12em;margin:0 0 14px;">What you get</p>
          {"".join([
              f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">'
              f'<div style="width:22px;height:22px;border-radius:6px;background:{bg};'
              f'border:1px solid {brd};display:flex;align-items:center;'
              f'justify-content:center;flex-shrink:0;font-size:.7rem;">{icon}</div>'
              f'<span style="font-family:Outfit,sans-serif;font-size:.82rem;color:#EEEAF8;">{txt}</span></div>'
              for icon, txt, bg, brd in [
                  ("🖼️", "Full-resolution PNG artwork", "rgba(167,139,250,.08)", "rgba(167,139,250,.2)"),
                  ("↔️", "Side-by-side comparison image", "rgba(96,165,250,.08)", "rgba(96,165,250,.2)"),
                  ("🚫", "No watermarks whatsoever", "rgba(52,211,153,.08)", "rgba(52,211,153,.2)"),
                  ("♾️", "Re-download anytime (30 days)", "rgba(244,114,182,.08)", "rgba(244,114,182,.2)"),
              ]
          ])}
        </div>
        """, unsafe_allow_html=True)

        # ── Razorpay button (via HTML component) ──────────────────────────────
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        _label("05 / Pay & Download")

        # Check if we already have a pending order in session
        if "payment_order" not in st.session_state:
            if st.button(
                f"Pay ₹{PRICE_PER_DOWNLOAD_INR} with Razorpay",
                type="primary",
                use_container_width=True,
                key="initiate_payment",
            ):
                with st.spinner("Creating secure order…"):
                    order_result = create_order(
                        amount_inr = PRICE_PER_DOWNLOAD_INR,
                        user_id    = user.get("user_id", 0),
                        image_ref  = os.path.basename(proc_path),
                    )
                if order_result["success"]:
                    st.session_state["payment_order"] = order_result
                    st.rerun()
                else:
                    st.error(f"Could not create order: {order_result['message']}")
        else:
            order = st.session_state["payment_order"]
            _render_razorpay_widget(order, user)

        # ── Demo / test-mode bypass ───────────────────────────────────────────
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(251,191,36,.04);border:1px solid rgba(251,191,36,.12);
                    border-radius:10px;padding:12px 16px;">
          <p style="font-family:'Syne Mono',monospace;font-size:.56rem;color:rgba(251,191,36,.6);
                    text-transform:uppercase;letter-spacing:.08em;margin:0 0 5px;">Test / Demo Mode</p>
          <p style="font-family:'Outfit',sans-serif;font-size:.78rem;color:#7C7A9A;margin:0;">
            Using test API keys? Click the button below to simulate a successful payment
            and test the full download flow without real money.
          </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Simulate Successful Payment (Demo)", use_container_width=True, key="demo_pay"):
            _handle_demo_payment(user, proc_path, result_style)


def _render_razorpay_widget(order: dict, user: dict):
    """Embed the Razorpay checkout JS widget via st.components.html."""
    order_id   = order["order_id"]
    amount     = order["amount"]       # paise
    key_id     = order["key_id"]
    uname      = user.get("username", "User")
    email      = user.get("email", "user@example.com")

    st.markdown(f"""
    <div style="background:rgba(167,139,250,.05);border:1px solid rgba(167,139,250,.18);
                border-left:3px solid #A78BFA;border-radius:10px;padding:12px 16px;
                margin-bottom:12px;">
      <p style="font-family:'Syne',sans-serif;font-weight:700;color:#EEEAF8;margin:0 0 3px;font-size:.88rem;">
        Order Ready
      </p>
      <p style="font-family:'Syne Mono',monospace;color:#3E3C58;margin:0;font-size:.62rem;">
        {order_id}
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Razorpay JS checkout widget
    components.html(f"""
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <style>
      body {{ margin:0; background:transparent; font-family:'Outfit',sans-serif; }}
      #rzp-btn {{
        width:100%; padding:14px 0; border:none; border-radius:10px; cursor:pointer;
        background:linear-gradient(135deg,#A78BFA,#F472B6); color:#fff;
        font-family:'Outfit',sans-serif; font-size:1rem; font-weight:700;
        letter-spacing:.02em;
        box-shadow:0 4px 24px rgba(167,139,250,.4);
        transition:transform .18s,box-shadow .18s;
      }}
      #rzp-btn:hover {{ transform:translateY(-2px); box-shadow:0 8px 36px rgba(167,139,250,.55); }}
      #rzp-btn:active {{ transform:translateY(0); }}
      #status {{ margin-top:10px; font-size:.78rem; color:#34D399; display:none; text-align:center; }}
    </style>
    <button id="rzp-btn" onclick="openRazorpay()">
      Open Razorpay &nbsp;·&nbsp; ₹{amount // 100}
    </button>
    <div id="status">✓ Payment captured – redirecting…</div>

    <script>
    function openRazorpay() {{
      var options = {{
        key:         "{key_id}",
        amount:      "{amount}",
        currency:    "INR",
        name:        "CartoonizeMe",
        description: "Artwork Download",
        order_id:    "{order_id}",
        prefill:     {{ name: "{uname}", email: "{email}" }},
        theme:       {{ color: "#A78BFA" }},
        handler: function(response) {{
          // Post payment details back to Streamlit parent via URL params
          var params = new URLSearchParams(window.location.search);
          // Use window.parent.postMessage to communicate
          window.parent.postMessage({{
            type:               "razorpay_success",
            razorpay_order_id:   response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature:  response.razorpay_signature,
          }}, "*");
          document.getElementById("rzp-btn").style.display = "none";
          document.getElementById("status").style.display  = "block";
        }},
        modal: {{
          ondismiss: function() {{
            window.parent.postMessage({{ type: "razorpay_dismissed" }}, "*");
          }}
        }}
      }};
      var rzp = new Razorpay(options);
      rzp.open();
    }}
    </script>
    """, height=80)

    # Manual payment confirmation form (fallback for postMessage limitations)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    with st.expander("Completed payment? Enter confirmation details here"):
        st.markdown("""
        <p style="font-family:'Outfit',sans-serif;font-size:.78rem;color:#7C7A9A;margin:0 0 10px;">
        After completing the Razorpay popup, paste your Payment ID below to unlock your download.
        </p>
        """, unsafe_allow_html=True)
        payment_id = st.text_input(
            "Razorpay Payment ID",
            placeholder="pay_XXXXXXXXXXXXXXXX",
            key="manual_payment_id",
        )
        signature  = st.text_input(
            "Razorpay Signature (optional)",
            placeholder="Leave blank for test mode",
            key="manual_signature",
            type="password",
        )
        if st.button("Verify & Unlock Download", type="primary", key="manual_verify"):
            if not payment_id:
                st.error("Please enter your Payment ID.")
            else:
                _process_verified_payment(
                    order_id   = order["order_id"],
                    payment_id = payment_id.strip(),
                    signature  = signature.strip() or "demo_signature",
                )


def _process_verified_payment(order_id: str, payment_id: str, signature: str):
    """Verify signature, update DB, transition to success page."""
    verified = verify_payment(order_id, payment_id, signature)
    if verified:
        save_transaction(order_id, payment_id, signature, status="paid")
        st.session_state.update({
            "payment_verified":    True,
            "paid_order_id":       order_id,
            "paid_payment_id":     payment_id,
            "page":                "payment_success",
        })
        st.session_state.pop("payment_order", None)
        st.rerun()
    else:
        st.error("Payment verification failed. Please check your Payment ID or contact support.")


def _handle_demo_payment(user: dict, proc_path: str, style: str):
    """Simulate a full payment for demo/testing purposes."""
    demo_order_id   = f"order_DEMO_{uuid.uuid4().hex[:16].upper()}"
    demo_payment_id = f"pay_DEMO_{uuid.uuid4().hex[:16].upper()}"
    demo_signature  = "demo_signature_for_testing"

    # Create DB record
    conn = __import__("database.db", fromlist=["get_connection"]).get_connection()
    conn.execute(
        """INSERT OR IGNORE INTO Transactions
           (user_id, razorpay_order_id, amount, currency, status, image_ref, receipt)
           VALUES (?, ?, ?, 'INR', 'paid', ?, ?)""",
        (user.get("user_id", 0), demo_order_id,
         PRICE_PER_DOWNLOAD_INR,
         os.path.basename(proc_path),
         f"rcpt_demo_{uuid.uuid4().hex[:8]}"),
    )
    conn.execute(
        """UPDATE Transactions
           SET razorpay_payment_id=?, razorpay_signature=?, status='paid', paid_at=CURRENT_TIMESTAMP
           WHERE razorpay_order_id=?""",
        (demo_payment_id, demo_signature, demo_order_id),
    )
    conn.commit()
    conn.close()

    st.session_state.update({
        "payment_verified": True,
        "paid_order_id":    demo_order_id,
        "paid_payment_id":  demo_payment_id,
        "page":             "payment_success",
    })
    st.session_state.pop("payment_order", None)
    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# SUCCESS PAGE
# ═══════════════════════════════════════════════════════════════════════════════

def show_payment_success():
    user        = st.session_state.get("user", {})
    proc_path   = st.session_state.get("proc_path", "")
    orig_path   = st.session_state.get("orig_path", "")
    order_id    = st.session_state.get("paid_order_id", "-")
    payment_id  = st.session_state.get("paid_payment_id", "-")
    result_style = st.session_state.get("result_style", "Artwork")

    # ── Animated success header ───────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center;padding:32px 0 24px;margin-bottom:8px;">
      <div style="display:inline-flex;align-items:center;justify-content:center;
                  width:64px;height:64px;border-radius:50%;
                  background:rgba(52,211,153,.1);border:2px solid rgba(52,211,153,.35);
                  margin-bottom:16px;font-size:1.8rem;
                  box-shadow:0 0 32px rgba(52,211,153,.2);">✓</div>
      <p style="font-family:'Syne Mono',monospace;font-size:.58rem;color:#34D399;
                text-transform:uppercase;letter-spacing:.18em;margin:0 0 8px;">Payment Confirmed</p>
      <h2 style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
                 color:#EEEAF8;margin:0 0 8px;letter-spacing:-.04em;">Your artwork is ready!</h2>
      <p style="font-family:'Outfit',sans-serif;font-size:.9rem;color:#7C7A9A;margin:0;">
        Transaction · <span style="color:#A78BFA;font-family:'Syne Mono',monospace;
                              font-size:.78rem;">{payment_id[:24]}…</span>
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Downloads ─────────────────────────────────────────────────────────────
    if proc_path and os.path.exists(proc_path):
        try:
            result_img = Image.open(proc_path)
            orig_img   = Image.open(orig_path) if orig_path and os.path.exists(orig_path) else None
        except Exception:
            result_img = None
            orig_img   = None

        if result_img:
            mark_downloaded(order_id)

            # Preview
            col_prev, col_info = st.columns([1, 1.5])
            with col_prev:
                st.image(result_img, use_container_width=True)
            with col_info:
                st.markdown(f"""
                <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.07);
                            border-radius:14px;padding:20px;height:100%;">
                  <p style="font-family:'Syne Mono',monospace;font-size:.56rem;color:#3E3C58;
                             text-transform:uppercase;letter-spacing:.1em;margin:0 0 16px;">Receipt</p>
                  {"".join([
                      f'<div style="padding:8px 0;border-bottom:1px solid rgba(255,255,255,.04);">'
                      f'<p style="font-family:Syne Mono,monospace;font-size:.56rem;color:#3E3C58;'
                      f'text-transform:uppercase;letter-spacing:.08em;margin:0 0 2px;">{lbl}</p>'
                      f'<p style="font-family:Outfit,sans-serif;font-size:.85rem;'
                      f'color:#EEEAF8;margin:0;font-weight:600;">{val}</p></div>'
                      for lbl, val in [
                          ("Order ID",    order_id[:32] + ("…" if len(order_id) > 32 else "")),
                          ("Payment ID",  payment_id[:28] + ("…" if len(payment_id) > 28 else "")),
                          ("Effect",      result_style.split(" ",1)[-1] if " " in result_style else result_style),
                          ("Amount Paid", f"₹{PRICE_PER_DOWNLOAD_INR}"),
                          ("Status",      "✓ Paid"),
                      ]
                  ])}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            _label("Download Your Files")

            d1, d2, d3 = st.columns(3)

            # Full-res artwork
            with d1:
                buf = io.BytesIO()
                result_img.save(buf, "PNG")
                style_slug = result_style.split()[-1].lower() if result_style else "art"
                st.download_button(
                    "⬇ Download Artwork",
                    data      = buf.getvalue(),
                    file_name = f"cartoonize_{style_slug}_{uuid.uuid4().hex[:6]}.png",
                    mime      = "image/png",
                    type      = "primary",
                    use_container_width=True,
                    key       = "dl_artwork",
                )

            # Comparison
            with d2:
                if orig_img:
                    from backend.image_processor import create_comparison
                    comp = create_comparison(orig_img, result_img, result_style)
                    cbuf = io.BytesIO()
                    comp.save(cbuf, "PNG")
                    st.download_button(
                        "↔ Comparison",
                        data      = cbuf.getvalue(),
                        file_name = "comparison.png",
                        mime      = "image/png",
                        use_container_width=True,
                        key       = "dl_comparison",
                    )
                else:
                    st.button("↔ Comparison", disabled=True, use_container_width=True)

            # JPG version
            with d3:
                jbuf = io.BytesIO()
                result_img.convert("RGB").save(jbuf, "JPEG", quality=92)
                st.download_button(
                    "⬇ JPG Version",
                    data      = jbuf.getvalue(),
                    file_name = f"cartoonize_{style_slug}.jpg",
                    mime      = "image/jpeg",
                    use_container_width=True,
                    key       = "dl_jpg",
                )
    else:
        st.warning("Processed image file not found on disk — it may have been cleaned up.")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Next actions ──────────────────────────────────────────────────────────
    st.markdown("""
    <p style="font-family:'Syne Mono',monospace;font-size:.58rem;color:#3E3C58;
              text-transform:uppercase;letter-spacing:.18em;margin:0 0 12px;">What next?</p>
    """, unsafe_allow_html=True)

    n1, n2, n3 = st.columns(3)
    with n1:
        if st.button("🎨 Create Another", use_container_width=True, key="next_create"):
            for k in ["result_img","result_style","result_elapsed",
                      "proc_path","orig_path","payment_verified",
                      "paid_order_id","paid_payment_id","payment_order"]:
                st.session_state.pop(k, None)
            st.session_state["page"] = "image_processing"
            st.rerun()
    with n2:
        if st.button("📂 My Gallery", use_container_width=True, key="next_gallery"):
            st.session_state["page"] = "history"
            st.rerun()
    with n3:
        if st.button("📋 Payment History", use_container_width=True, key="next_txhist"):
            st.session_state["page"] = "payment_history"
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# FAILURE PAGE
# ═══════════════════════════════════════════════════════════════════════════════

def show_payment_failure():
    back_button("Back to Checkout", "payment")

    st.markdown("""
    <div style="text-align:center;padding:36px 0 28px;max-width:520px;margin:0 auto;">
      <div style="display:inline-flex;align-items:center;justify-content:center;
                  width:64px;height:64px;border-radius:50%;
                  background:rgba(244,114,182,.08);border:2px solid rgba(244,114,182,.3);
                  margin-bottom:16px;font-size:1.8rem;
                  box-shadow:0 0 28px rgba(244,114,182,.15);">✗</div>
      <p style="font-family:'Syne Mono',monospace;font-size:.58rem;color:#F472B6;
                text-transform:uppercase;letter-spacing:.18em;margin:0 0 8px;">Payment Failed</p>
      <h2 style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;
                 color:#EEEAF8;margin:0 0 12px;letter-spacing:-.04em;">Something went wrong</h2>
      <p style="font-family:'Outfit',sans-serif;font-size:.9rem;color:#7C7A9A;
                line-height:1.65;margin:0 0 28px;">
        Your payment could not be processed. No money was charged.
        You can try again or contact our support team.
      </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Try Again", type="primary", use_container_width=True, key="fail_retry"):
            st.session_state.pop("payment_order", None)
            st.session_state["page"] = "payment"
            st.rerun()
    with c2:
        if st.button("Back to Studio", use_container_width=True, key="fail_studio"):
            st.session_state["page"] = "image_processing"
            st.rerun()

    st.markdown("""
    <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.06);
                border-radius:12px;padding:18px;margin-top:28px;max-width:520px;">
      <p style="font-family:'Syne Mono',monospace;font-size:.56rem;color:#3E3C58;
                text-transform:uppercase;letter-spacing:.1em;margin:0 0 10px;">Common Reasons</p>
      <ul style="font-family:'Outfit',sans-serif;font-size:.82rem;color:#7C7A9A;
                 margin:0;padding-left:18px;line-height:2;">
        <li>Card declined or insufficient funds</li>
        <li>Network timeout during payment</li>
        <li>Bank blocked the transaction</li>
        <li>Incorrect card details entered</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAYMENT HISTORY PAGE
# ═══════════════════════════════════════════════════════════════════════════════

def show_payment_history():
    back_button("Back", "dashboard")
    user = st.session_state.get("user", {})

    st.markdown("""
    <div style="margin-bottom:24px;">
      <p style="font-family:'Syne Mono',monospace;font-size:.58rem;color:#3E3C58;
                text-transform:uppercase;letter-spacing:.18em;margin:0 0 8px;">Billing</p>
      <h2 style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
                 color:#EEEAF8;margin:0;letter-spacing:-.04em;">Payment History</h2>
    </div>
    """, unsafe_allow_html=True)

    transactions = get_user_transactions(user.get("user_id", 0))

    if not transactions:
        st.markdown("""
        <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.06);
                    border-radius:16px;padding:60px;text-align:center;">
          <p style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;
                    color:#3E3C58;margin:0 0 6px;">No transactions yet</p>
          <p style="font-family:'Outfit',sans-serif;font-size:.85rem;color:#3E3C58;margin:0;">
            Download an artwork to see your payment history here
          </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("Go to Art Studio", type="primary", key="ph_cta"):
            st.session_state["page"] = "image_processing"
            st.rerun()
        return

    # Summary stats
    paid_txs   = [t for t in transactions if t.get("status") == "paid"]
    total_paid = sum(t.get("amount", 0) for t in paid_txs)

    sc1, sc2, sc3 = st.columns(3)
    for col, val, lbl, color in [
        (sc1, len(transactions),  "Total Orders",    "#A78BFA"),
        (sc2, len(paid_txs),      "Successful",      "#34D399"),
        (sc3, f"₹{total_paid}",   "Total Spent",     "#F472B6"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.06);
                        border-radius:12px;padding:16px;margin-bottom:16px;">
              <p style="font-family:'Syne',sans-serif;font-weight:800;
                         font-size:1.5rem;color:#EEEAF8;margin:0;">{val}</p>
              <p style="font-family:'Syne Mono',monospace;font-size:.55rem;
                         color:{color};text-transform:uppercase;
                         letter-spacing:.1em;margin:5px 0 0;">{lbl}</p>
            </div>
            """, unsafe_allow_html=True)

    # Transaction table
    st.markdown("""
    <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.06);
                border-radius:16px;overflow:hidden;">
      <div style="padding:16px 20px;border-bottom:1px solid rgba(255,255,255,.05);
                  display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;gap:12px;">
        <span style="font-family:'Syne Mono',monospace;font-size:.55rem;color:#3E3C58;
                     text-transform:uppercase;letter-spacing:.1em;">Order ID</span>
        <span style="font-family:'Syne Mono',monospace;font-size:.55rem;color:#3E3C58;
                     text-transform:uppercase;letter-spacing:.1em;">Amount</span>
        <span style="font-family:'Syne Mono',monospace;font-size:.55rem;color:#3E3C58;
                     text-transform:uppercase;letter-spacing:.1em;">Status</span>
        <span style="font-family:'Syne Mono',monospace;font-size:.55rem;color:#3E3C58;
                     text-transform:uppercase;letter-spacing:.1em;">Effect</span>
        <span style="font-family:'Syne Mono',monospace;font-size:.55rem;color:#3E3C58;
                     text-transform:uppercase;letter-spacing:.1em;">Date</span>
      </div>
    """, unsafe_allow_html=True)

    STATUS_COLORS = {
        "paid":    ("#34D399", "rgba(52,211,153,.08)",  "rgba(52,211,153,.2)"),
        "created": ("#FBBF24", "rgba(251,191,36,.08)",  "rgba(251,191,36,.2)"),
        "failed":  ("#F472B6", "rgba(244,114,182,.08)", "rgba(244,114,182,.2)"),
    }

    for i, tx in enumerate(transactions):
        status     = tx.get("status", "created")
        sc, sbg, sbrd = STATUS_COLORS.get(status, ("#7C7A9A","rgba(255,255,255,.04)","rgba(255,255,255,.1)"))
        order_id   = (tx.get("razorpay_order_id") or "-")
        order_short = order_id[:20] + "…" if len(order_id) > 20 else order_id
        amount     = f"₹{tx.get('amount', 0)}"
        image_ref  = tx.get("image_ref") or "-"
        date       = (tx.get("created_at") or "")[:16]
        border     = "border-bottom:1px solid rgba(255,255,255,.04);" if i < len(transactions)-1 else ""

        st.markdown(f"""
        <div style="padding:14px 20px;{border}
                    display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;gap:12px;
                    align-items:center;">
          <span style="font-family:'Syne Mono',monospace;font-size:.62rem;color:#7C7A9A;
                       overflow:hidden;text-overflow:ellipsis;">{order_short}</span>
          <span style="font-family:'Outfit',sans-serif;font-size:.85rem;
                       color:#EEEAF8;font-weight:600;">{amount}</span>
          <span style="display:inline-flex;align-items:center;justify-content:center;
                       font-family:'Syne Mono',monospace;font-size:.54rem;
                       color:{sc};text-transform:uppercase;letter-spacing:.06em;
                       background:{sbg};border:1px solid {sbrd};
                       border-radius:99px;padding:3px 9px;">{status}</span>
          <span style="font-family:'Outfit',sans-serif;font-size:.78rem;
                       color:#7C7A9A;">{image_ref[:18]}</span>
          <span style="font-family:'Syne Mono',monospace;font-size:.58rem;
                       color:#3E3C58;">{date}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)