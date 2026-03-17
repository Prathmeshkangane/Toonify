"""
frontend/payment_page.py — Upgraded UI
Full Razorpay payment flow with premium dark UI
"""

import streamlit as st
import streamlit.components.v1 as components
import sys, os, io, uuid, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PIL import Image

try:
    from utils.styles import back_button
except ImportError:
    def back_button(label, page):
        if st.button(f"← {label}", key="back_nav"):
            st.session_state["page"] = page
            st.rerun()

try:
    from payment.razorpay_handler import (
        create_order, verify_payment, save_transaction,
        get_transaction, get_user_transactions, mark_downloaded,
        is_payment_verified, RAZORPAY_KEY_ID, PRICE_PER_DOWNLOAD_INR,
    )
except ImportError as e:
    st.error(f"Payment module not found: {e}")
    st.stop()


def _page_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Outfit:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

    html, body, .stApp { background:#06060E !important; }
    #MainMenu, footer, header[data-testid="stHeader"],
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] { display:none !important; }
    .block-container { padding: 24px 32px 48px !important; max-width: 1300px !important; }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg,#9370DB,#C471ED) !important;
        color: #fff !important; border: none !important;
        border-radius: 12px !important; height: 48px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important; font-size: .9rem !important;
        box-shadow: 0 4px 20px rgba(147,112,219,.3) !important;
        transition: all .2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 32px rgba(147,112,219,.45) !important;
    }
    .stButton > button:not([kind="primary"]) {
        background: rgba(255,255,255,.03) !important;
        color: rgba(255,255,255,.55) !important;
        border: 1px solid rgba(255,255,255,.08) !important;
        border-radius: 12px !important; height: 46px !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: .85rem !important; transition: all .18s ease !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        border-color: rgba(147,112,219,.3) !important;
        color: #C471ED !important;
        background: rgba(147,112,219,.05) !important;
        transform: translateY(-1px) !important;
    }
    .stDownloadButton > button {
        background: linear-gradient(135deg,rgba(147,112,219,.12),rgba(196,113,237,.08)) !important;
        border: 1px solid rgba(147,112,219,.2) !important;
        color: #C471ED !important;
        border-radius: 12px !important; height: 46px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important; font-size: .85rem !important;
        transition: all .18s ease !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg,rgba(147,112,219,.2),rgba(196,113,237,.14)) !important;
        transform: translateY(-1px) !important;
    }
    .stTextInput > div > div > input {
        background: rgba(255,255,255,.035) !important;
        border: 1px solid rgba(255,255,255,.08) !important;
        border-radius: 12px !important;
        color: #F0ECF8 !important;
        padding: 12px 16px !important;
        font-family: 'Outfit', sans-serif !important;
        height: 46px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(147,112,219,.5) !important;
        box-shadow: 0 0 0 3px rgba(147,112,219,.08) !important;
        outline: none !important;
    }
    .stTextInput label {
        font-family: 'Space Mono', monospace !important;
        font-size: .62rem !important;
        color: rgba(255,255,255,.28) !important;
        text-transform: uppercase !important;
        letter-spacing: .12em !important;
    }
    .stExpander {
        background: rgba(255,255,255,.02) !important;
        border: 1px solid rgba(255,255,255,.07) !important;
        border-radius: 14px !important;
    }
    </style>
    """, unsafe_allow_html=True)


def _label(text, color="rgba(255,255,255,.2)"):
    st.markdown(
        f'<p style="font-family:Space Mono,monospace;font-size:.6rem;color:{color};'
        f'text-transform:uppercase;letter-spacing:.16em;margin:0 0 10px;">{text}</p>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# CHECKOUT PAGE
# ══════════════════════════════════════════════════════════════════════════════

def show_payment_page():
    _page_styles()
    back_button("Back to Studio", "image_processing")
    user = st.session_state.get("user", {})

    if "proc_path" not in st.session_state:
        st.markdown("""
        <div style="background:#0A0A14;border:1px solid rgba(251,191,36,.15);
                    border-radius:16px;padding:32px;text-align:center;max-width:520px;margin:0 auto;">
          <div style="font-size:2rem;margin-bottom:14px;">⚠️</div>
          <p style="font-family:'Syne',sans-serif;font-weight:700;color:#F0ECF8;font-size:1rem;margin:0 0 8px;">
            No processed image found
          </p>
          <p style="font-family:'Outfit',sans-serif;font-size:.85rem;color:rgba(255,255,255,.35);margin:0;">
            Please create an artwork in Art Studio first
          </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        if st.button("Go to Art Studio 🎨", type="primary"):
            st.session_state["page"] = "image_processing"
            st.rerun()
        return

    result_style   = st.session_state.get("result_style", "Unknown Effect")
    proc_path      = st.session_state.get("proc_path", "")
    orig_path      = st.session_state.get("orig_path", "")
    result_elapsed = st.session_state.get("result_elapsed", 0)

    # Page header
    st.markdown("""
    <div style="margin-bottom:32px;padding-bottom:20px;border-bottom:1px solid rgba(255,255,255,.05);">
      <p style="font-family:'Space Mono',monospace;font-size:.6rem;color:rgba(147,112,219,.6);
                text-transform:uppercase;letter-spacing:.18em;margin:0 0 8px;">Checkout</p>
      <h2 style="font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;
                 color:#F0ECF8;margin:0;letter-spacing:-.05em;">Download Your Artwork</h2>
    </div>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 1.4])

    with left_col:
        _label("Your Artwork", "rgba(147,112,219,.6)")

        st.markdown("""
        <div style="border-radius:16px;overflow:hidden;
                    border:1px solid rgba(147,112,219,.15);
                    box-shadow:0 8px 32px rgba(0,0,0,.4);">
        """, unsafe_allow_html=True)
        if proc_path and os.path.exists(proc_path):
            st.image(proc_path, use_container_width=True)
        else:
            st.markdown("""
            <div style="aspect-ratio:1;background:#0A0A14;display:flex;
                        align-items:center;justify-content:center;font-size:3rem;">🖼️</div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Order summary
        style_short = result_style.split(" ", 1)[-1] if " " in result_style else result_style
        summary_rows = "".join([
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:9px 0;{("border-bottom:1px solid rgba(255,255,255,.04);" if i < 3 else "")}">'
            f'<span style="font-family:Outfit,sans-serif;font-size:.81rem;color:rgba(255,255,255,.3);">{lbl}</span>'
            f'<span style="font-family:Space Mono,monospace;font-size:.76rem;color:#F0ECF8;">{val}</span></div>'
            for i, (lbl, val) in enumerate([
                ("Effect", style_short),
                ("Format", "PNG — Full Quality"),
                ("Processing", f"{result_elapsed}s"),
                ("Includes", "Comparison Image"),
            ])
        ])
        st.markdown(f"""
        <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.07);
                    border-radius:16px;padding:18px;margin-top:16px;">
          <p style="font-family:'Space Mono',monospace;font-size:.56rem;color:rgba(255,255,255,.2);
                    text-transform:uppercase;letter-spacing:.12em;margin:0 0 14px;">Order Summary</p>
          {summary_rows}
          <div style="display:flex;justify-content:space-between;align-items:center;padding:14px 0 2px;">
            <span style="font-family:'Syne',sans-serif;font-weight:700;font-size:.9rem;color:#F0ECF8;">Total</span>
            <span style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.5rem;
                         background:linear-gradient(135deg,#9370DB,#C471ED);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                         background-clip:text;">₹{PRICE_PER_DOWNLOAD_INR}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        _label("Secure Payment", "rgba(52,211,153,.6)")

        # Trust badges
        st.markdown("""
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px;">
          <div style="display:flex;align-items:center;gap:6px;background:rgba(52,211,153,.05);
                      border:1px solid rgba(52,211,153,.14);border-radius:99px;padding:5px 12px;">
            <span style="font-size:.75rem;">🔒</span>
            <span style="font-family:Space Mono,monospace;font-size:.55rem;color:#34D399;
                         letter-spacing:.06em;text-transform:uppercase;">SSL Secured</span>
          </div>
          <div style="display:flex;align-items:center;gap:6px;background:rgba(147,112,219,.05);
                      border:1px solid rgba(147,112,219,.14);border-radius:99px;padding:5px 12px;">
            <span style="font-size:.75rem;">⚡</span>
            <span style="font-family:Space Mono,monospace;font-size:.55rem;color:#9370DB;
                         letter-spacing:.06em;text-transform:uppercase;">Instant Download</span>
          </div>
          <div style="display:flex;align-items:center;gap:6px;background:rgba(96,165,250,.05);
                      border:1px solid rgba(96,165,250,.14);border-radius:99px;padding:5px 12px;">
            <span style="font-size:.75rem;">✓</span>
            <span style="font-family:Space Mono,monospace;font-size:.55rem;color:#60A5FA;
                         letter-spacing:.06em;text-transform:uppercase;">Razorpay</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # What you get
        features = [
            ("🖼️", "Full-resolution PNG artwork",   "rgba(147,112,219,.07)", "rgba(147,112,219,.18)"),
            ("↔️", "Side-by-side comparison image",  "rgba(96,165,250,.07)",  "rgba(96,165,250,.18)"),
            ("🚫", "No watermarks whatsoever",        "rgba(52,211,153,.07)",  "rgba(52,211,153,.18)"),
            ("♾️", "Re-download anytime (30 days)",   "rgba(251,191,36,.07)", "rgba(251,191,36,.18)"),
        ]
        items = "".join([
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:11px;">'
            f'<div style="width:34px;height:34px;border-radius:10px;background:{bg};'
            f'border:1px solid {brd};display:flex;align-items:center;'
            f'justify-content:center;flex-shrink:0;font-size:.85rem;">{icon}</div>'
            f'<span style="font-family:Outfit,sans-serif;font-size:.83rem;color:rgba(255,255,255,.7);">{txt}</span></div>'
            for icon, txt, bg, brd in features
        ])
        st.markdown(f"""
        <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.07);
                    border-radius:16px;padding:18px;margin-bottom:20px;">
          <p style="font-family:'Space Mono',monospace;font-size:.56rem;color:rgba(255,255,255,.2);
                    text-transform:uppercase;letter-spacing:.12em;margin:0 0 16px;">What you get</p>
          {items}
        </div>
        """, unsafe_allow_html=True)

        _label("Pay & Download", "rgba(147,112,219,.6)")

        if "payment_order" not in st.session_state:
            if st.button(
                f"💳  Pay ₹{PRICE_PER_DOWNLOAD_INR} with Razorpay",
                type="primary", use_container_width=True, key="initiate_payment",
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

        # Demo mode
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(251,191,36,.04);border:1px solid rgba(251,191,36,.1);
                    border-radius:12px;padding:14px 18px;">
          <p style="font-family:'Space Mono',monospace;font-size:.56rem;color:rgba(251,191,36,.55);
                    text-transform:uppercase;letter-spacing:.08em;margin:0 0 6px;">Test / Demo Mode</p>
          <p style="font-family:'Outfit',sans-serif;font-size:.79rem;color:rgba(255,255,255,.3);margin:0;">
            Using test API keys? Simulate a successful payment to test the full download flow.
          </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("Simulate Successful Payment (Demo)", use_container_width=True, key="demo_pay"):
            _handle_demo_payment(user, proc_path, result_style)


def _render_razorpay_widget(order: dict, user: dict):
    order_id = order["order_id"]
    amount   = order["amount"]
    key_id   = order["key_id"]
    uname    = user.get("username", "User")
    email    = user.get("email", "user@example.com")

    st.markdown(f"""
    <div style="background:rgba(147,112,219,.05);border:1px solid rgba(147,112,219,.18);
                border-left:3px solid #9370DB;border-radius:12px;padding:13px 18px;
                margin-bottom:14px;">
      <p style="font-family:'Syne',sans-serif;font-weight:700;color:#F0ECF8;margin:0 0 3px;font-size:.88rem;">
        Order Ready ✓
      </p>
      <p style="font-family:'Space Mono',monospace;color:rgba(255,255,255,.25);margin:0;font-size:.6rem;">
        {order_id}
      </p>
    </div>
    """, unsafe_allow_html=True)

    components.html(f"""
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <style>
      body {{ margin:0; background:transparent; font-family:'Outfit',sans-serif; }}
      #rzp-btn {{
        width:100%; padding:15px 0; border:none; border-radius:12px; cursor:pointer;
        background:linear-gradient(135deg,#9370DB,#C471ED);
        color:#fff; font-size:1rem; font-weight:700; letter-spacing:.02em;
        box-shadow:0 4px 24px rgba(147,112,219,.4);
        transition:transform .18s,box-shadow .18s;
      }}
      #rzp-btn:hover {{ transform:translateY(-2px); box-shadow:0 8px 40px rgba(147,112,219,.55); }}
      #status {{ margin-top:10px; font-size:.78rem; color:#34D399; display:none; text-align:center;
                 font-family:'Space Mono',monospace; letter-spacing:.06em; }}
    </style>
    <button id="rzp-btn" onclick="openRazorpay()">
      💳 &nbsp; Open Razorpay &nbsp;·&nbsp; ₹{amount // 100}
    </button>
    <div id="status">✓ Payment captured — redirecting…</div>
    <script>
    function openRazorpay() {{
      var options = {{
        key: "{key_id}", amount: "{amount}", currency: "INR",
        name: "Toonify", description: "Artwork Download",
        order_id: "{order_id}",
        prefill: {{ name: "{uname}", email: "{email}" }},
        theme: {{ color: "#9370DB" }},
        handler: function(response) {{
          window.parent.postMessage({{
            type: "razorpay_success",
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
          }}, "*");
          document.getElementById("rzp-btn").style.display = "none";
          document.getElementById("status").style.display = "block";
        }},
        modal: {{ ondismiss: function() {{ window.parent.postMessage({{ type: "razorpay_dismissed" }}, "*"); }} }}
      }};
      var rzp = new Razorpay(options);
      rzp.open();
    }}
    </script>
    """, height=80)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    with st.expander("✅ Completed payment? Enter confirmation details here"):
        st.markdown("""
        <p style="font-family:'Outfit',sans-serif;font-size:.79rem;color:rgba(255,255,255,.3);margin:0 0 12px;">
        After completing the Razorpay popup, paste your Payment ID below to unlock your download.
        </p>
        """, unsafe_allow_html=True)
        payment_id = st.text_input("Razorpay Payment ID", placeholder="pay_XXXXXXXXXXXXXXXX", key="manual_payment_id")
        signature  = st.text_input("Razorpay Signature (optional)", placeholder="Leave blank for test mode",
                                   key="manual_signature", type="password")
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
    verified = verify_payment(order_id, payment_id, signature)
    if verified:
        save_transaction(order_id, payment_id, signature, status="paid")
        st.session_state.update({
            "payment_verified": True,
            "paid_order_id":    order_id,
            "paid_payment_id":  payment_id,
            "page":             "payment_success",
        })
        st.session_state.pop("payment_order", None)
        st.rerun()
    else:
        st.error("Payment verification failed. Please check your Payment ID or contact support.")


def _handle_demo_payment(user: dict, proc_path: str, style: str):
    demo_order_id   = f"order_DEMO_{uuid.uuid4().hex[:16].upper()}"
    demo_payment_id = f"pay_DEMO_{uuid.uuid4().hex[:16].upper()}"
    demo_signature  = "demo_signature_for_testing"

    conn = __import__("database.db", fromlist=["get_connection"]).get_connection()
    conn.execute(
        """INSERT OR IGNORE INTO Transactions
           (user_id, razorpay_order_id, amount, currency, status, image_ref, receipt)
           VALUES (?, ?, ?, 'INR', 'paid', ?, ?)""",
        (user.get("user_id", 0), demo_order_id, PRICE_PER_DOWNLOAD_INR,
         os.path.basename(proc_path), f"rcpt_demo_{uuid.uuid4().hex[:8]}"),
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


# ══════════════════════════════════════════════════════════════════════════════
# SUCCESS PAGE
# ══════════════════════════════════════════════════════════════════════════════

def show_payment_success():
    _page_styles()
    user         = st.session_state.get("user", {})
    proc_path    = st.session_state.get("proc_path", "")
    orig_path    = st.session_state.get("orig_path", "")
    order_id     = st.session_state.get("paid_order_id", "-")
    payment_id   = st.session_state.get("paid_payment_id", "-")
    result_style = st.session_state.get("result_style", "Artwork")

    # Success header
    st.markdown(f"""
    <div style="text-align:center;padding:40px 0 32px;margin-bottom:8px;">
      <!-- Animated check ring -->
      <div style="display:inline-flex;align-items:center;justify-content:center;
                  width:72px;height:72px;border-radius:50%;
                  background:rgba(52,211,153,.08);border:2px solid rgba(52,211,153,.3);
                  margin-bottom:20px;font-size:2rem;
                  box-shadow:0 0 40px rgba(52,211,153,.2);">✓</div>
      <p style="font-family:'Space Mono',monospace;font-size:.6rem;color:#34D399;
                text-transform:uppercase;letter-spacing:.18em;margin:0 0 10px;">Payment Confirmed</p>
      <h2 style="font-family:'Syne',sans-serif;font-size:2.4rem;font-weight:800;
                 color:#F0ECF8;margin:0 0 10px;letter-spacing:-.05em;">Your artwork is ready!</h2>
      <p style="font-family:'Outfit',sans-serif;font-size:.88rem;color:rgba(255,255,255,.3);margin:0;">
        Transaction ·&nbsp;
        <span style="color:#9370DB;font-family:'Space Mono',monospace;font-size:.76rem;">
          {payment_id[:24]}…
        </span>
      </p>
    </div>
    """, unsafe_allow_html=True)

    if proc_path and os.path.exists(proc_path):
        try:
            result_img = Image.open(proc_path)
            orig_img   = Image.open(orig_path) if orig_path and os.path.exists(orig_path) else None
        except Exception:
            result_img = None
            orig_img   = None

        if result_img:
            mark_downloaded(order_id)

            col_prev, col_info = st.columns([1, 1.5])
            with col_prev:
                st.markdown("""
                <div style="border-radius:16px;overflow:hidden;
                            border:1px solid rgba(147,112,219,.15);
                            box-shadow:0 8px 32px rgba(0,0,0,.5);">
                """, unsafe_allow_html=True)
                st.image(result_img, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_info:
                receipt_rows = "".join([
                    f'<div style="padding:11px 0;{("border-bottom:1px solid rgba(255,255,255,.04);" if i < 4 else "")}">'
                    f'<p style="font-family:Space Mono,monospace;font-size:.54rem;color:rgba(255,255,255,.22);'
                    f'text-transform:uppercase;letter-spacing:.1em;margin:0 0 3px;">{lbl}</p>'
                    f'<p style="font-family:Outfit,sans-serif;font-size:.88rem;'
                    f'color:#F0ECF8;margin:0;font-weight:600;">{val}</p></div>'
                    for i, (lbl, val) in enumerate([
                        ("Order ID",    order_id[:32] + ("…" if len(order_id) > 32 else "")),
                        ("Payment ID",  payment_id[:28] + ("…" if len(payment_id) > 28 else "")),
                        ("Effect",      result_style.split(" ",1)[-1] if " " in result_style else result_style),
                        ("Amount Paid", f"₹{PRICE_PER_DOWNLOAD_INR}"),
                        ("Status",      "✓ Paid"),
                    ])
                ])
                st.markdown(f"""
                <div style="background:#0A0A14;border:1px solid rgba(52,211,153,.15);
                            border-radius:16px;padding:20px 22px;height:100%;">
                  <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
                    <div style="width:8px;height:8px;border-radius:50%;background:#34D399;
                                box-shadow:0 0 8px rgba(52,211,153,.8);"></div>
                    <p style="font-family:'Space Mono',monospace;font-size:.56rem;color:#34D399;
                               text-transform:uppercase;letter-spacing:.12em;margin:0;">Receipt</p>
                  </div>
                  {receipt_rows}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
            _label("Download Your Files", "rgba(52,211,153,.6)")

            d1, d2, d3 = st.columns(3)

            with d1:
                buf = io.BytesIO()
                result_img.save(buf, "PNG")
                style_slug = result_style.split()[-1].lower() if result_style else "art"
                st.download_button(
                    "⬇ Download Artwork (PNG)",
                    data      = buf.getvalue(),
                    file_name = f"cartoonize_{style_slug}_{uuid.uuid4().hex[:6]}.png",
                    mime      = "image/png",
                    type      = "primary",
                    use_container_width=True,
                    key       = "dl_artwork",
                )

            with d2:
                if orig_img:
                    from backend.image_processor import create_comparison
                    comp = create_comparison(orig_img, result_img, result_style)
                    cbuf = io.BytesIO()
                    comp.save(cbuf, "PNG")
                    st.download_button(
                        "↔ Comparison Image",
                        data      = cbuf.getvalue(),
                        file_name = "comparison.png",
                        mime      = "image/png",
                        use_container_width=True,
                        key       = "dl_comparison",
                    )
                else:
                    st.button("↔ Comparison", disabled=True, use_container_width=True)

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

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    # Next actions
    st.markdown("""
    <p style="font-family:'Space Mono',monospace;font-size:.6rem;color:rgba(255,255,255,.2);
              text-transform:uppercase;letter-spacing:.18em;margin:0 0 14px;">What next?</p>
    """, unsafe_allow_html=True)

    n1, n2, n3 = st.columns(3)
    with n1:
        if st.button("🎨 Create Another", use_container_width=True, key="next_create"):
            for k in ["result_img","result_style","result_elapsed","proc_path","orig_path",
                      "payment_verified","paid_order_id","paid_payment_id","payment_order"]:
                st.session_state.pop(k, None)
            st.session_state["page"] = "image_processing"
            st.rerun()
    with n2:
        if st.button("🖼 My Gallery", use_container_width=True, key="next_gallery"):
            st.session_state["page"] = "history"
            st.rerun()
    with n3:
        if st.button("📋 Payment History", use_container_width=True, key="next_txhist"):
            st.session_state["page"] = "payment_history"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# FAILURE PAGE
# ══════════════════════════════════════════════════════════════════════════════

def show_payment_failure():
    _page_styles()
    back_button("Back to Checkout", "payment")

    st.markdown("""
    <div style="text-align:center;padding:44px 0 32px;max-width:520px;margin:0 auto;">
      <div style="display:inline-flex;align-items:center;justify-content:center;
                  width:72px;height:72px;border-radius:50%;
                  background:rgba(246,79,89,.08);border:2px solid rgba(246,79,89,.25);
                  margin-bottom:20px;font-size:2rem;
                  box-shadow:0 0 32px rgba(246,79,89,.12);">✕</div>
      <p style="font-family:'Space Mono',monospace;font-size:.6rem;color:#F64F59;
                text-transform:uppercase;letter-spacing:.18em;margin:0 0 10px;">Payment Failed</p>
      <h2 style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
                 color:#F0ECF8;margin:0 0 14px;letter-spacing:-.05em;">Something went wrong</h2>
      <p style="font-family:'Outfit',sans-serif;font-size:.9rem;color:rgba(255,255,255,.35);
                line-height:1.65;margin:0 0 32px;">
        Your payment could not be processed.<br>No money was charged. You can try again.
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

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.06);
                border-radius:16px;padding:20px 24px;max-width:520px;">
      <p style="font-family:'Space Mono',monospace;font-size:.56rem;color:rgba(255,255,255,.2);
                text-transform:uppercase;letter-spacing:.1em;margin:0 0 12px;">Common Reasons</p>
      <ul style="font-family:'Outfit',sans-serif;font-size:.82rem;color:rgba(255,255,255,.35);
                 margin:0;padding-left:18px;line-height:2.2;">
        <li>Card declined or insufficient funds</li>
        <li>Network timeout during payment</li>
        <li>Bank blocked the transaction</li>
        <li>Incorrect card details entered</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAYMENT HISTORY
# ══════════════════════════════════════════════════════════════════════════════

def show_payment_history():
    _page_styles()
    back_button("Back", "dashboard")
    user = st.session_state.get("user", {})

    st.markdown("""
    <div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid rgba(255,255,255,.05);">
      <p style="font-family:'Space Mono',monospace;font-size:.6rem;color:rgba(147,112,219,.6);
                text-transform:uppercase;letter-spacing:.18em;margin:0 0 8px;">Billing</p>
      <h2 style="font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;
                 color:#F0ECF8;margin:0;letter-spacing:-.05em;">Payment History</h2>
    </div>
    """, unsafe_allow_html=True)

    transactions = get_user_transactions(user.get("user_id", 0))

    if not transactions:
        st.markdown("""
        <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.06);
                    border-radius:20px;padding:70px;text-align:center;">
          <div style="font-size:3rem;margin-bottom:18px;opacity:.2;">💳</div>
          <p style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;
                    color:rgba(255,255,255,.25);margin:0 0 8px;">No transactions yet</p>
          <p style="font-family:'Outfit',sans-serif;font-size:.85rem;
                    color:rgba(255,255,255,.18);margin:0 0 24px;">
            Download an artwork to see your payment history here
          </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        if st.button("Go to Art Studio 🎨", type="primary", key="ph_cta"):
            st.session_state["page"] = "image_processing"
            st.rerun()
        return

    paid_txs   = [t for t in transactions if t.get("status") == "paid"]
    total_paid = sum(t.get("amount", 0) for t in paid_txs)

    # Summary cards
    sc1, sc2, sc3 = st.columns(3)
    for col, val, lbl, color, bg, brd in [
        (sc1, len(transactions), "Total Orders",  "#9370DB", "rgba(147,112,219,.07)", "rgba(147,112,219,.15)"),
        (sc2, len(paid_txs),    "Successful",     "#34D399", "rgba(52,211,153,.07)",  "rgba(52,211,153,.15)"),
        (sc3, f"₹{total_paid}", "Total Spent",    "#C471ED", "rgba(196,113,237,.07)", "rgba(196,113,237,.15)"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {brd};
                        border-radius:16px;padding:18px;margin-bottom:20px;
                        position:relative;overflow:hidden;">
              <div style="position:absolute;top:-14px;right:-14px;width:60px;height:60px;
                          background:radial-gradient(circle,{brd} 0%,transparent 70%);
                          border-radius:50%;pointer-events:none;"></div>
              <p style="font-family:'Syne',sans-serif;font-weight:800;
                         font-size:1.6rem;color:#F0ECF8;margin:0;">{val}</p>
              <p style="font-family:'Space Mono',monospace;font-size:.55rem;
                         color:{color};text-transform:uppercase;letter-spacing:.1em;margin:7px 0 0;">{lbl}</p>
            </div>
            """, unsafe_allow_html=True)

    # Transaction table
    STATUS_CFG = {
        "paid":    ("#34D399", "rgba(52,211,153,.08)",  "rgba(52,211,153,.2)"),
        "created": ("#FBBF24", "rgba(251,191,36,.08)",  "rgba(251,191,36,.2)"),
        "failed":  ("#F64F59", "rgba(246,79,89,.08)",   "rgba(246,79,89,.2)"),
    }

    st.markdown("""
    <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.06);
                border-radius:18px;overflow:hidden;">
      <div style="padding:16px 22px;border-bottom:1px solid rgba(255,255,255,.05);
                  display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;gap:12px;">
        <span style="font-family:'Space Mono',monospace;font-size:.54rem;color:rgba(255,255,255,.2);
                     text-transform:uppercase;letter-spacing:.1em;">Order ID</span>
        <span style="font-family:'Space Mono',monospace;font-size:.54rem;color:rgba(255,255,255,.2);
                     text-transform:uppercase;letter-spacing:.1em;">Amount</span>
        <span style="font-family:'Space Mono',monospace;font-size:.54rem;color:rgba(255,255,255,.2);
                     text-transform:uppercase;letter-spacing:.1em;">Status</span>
        <span style="font-family:'Space Mono',monospace;font-size:.54rem;color:rgba(255,255,255,.2);
                     text-transform:uppercase;letter-spacing:.1em;">Image</span>
        <span style="font-family:'Space Mono',monospace;font-size:.54rem;color:rgba(255,255,255,.2);
                     text-transform:uppercase;letter-spacing:.1em;">Date</span>
      </div>
    """, unsafe_allow_html=True)

    for i, tx in enumerate(transactions):
        status     = tx.get("status", "created")
        sc, sbg, sbrd = STATUS_CFG.get(status, ("#7C7A9A","rgba(255,255,255,.04)","rgba(255,255,255,.1)"))
        order_id   = (tx.get("razorpay_order_id") or "-")
        order_short = order_id[:20] + "…" if len(order_id) > 20 else order_id
        amount     = f"₹{tx.get('amount', 0)}"
        image_ref  = tx.get("image_ref") or "-"
        date       = (tx.get("created_at") or "")[:16]
        border     = "border-bottom:1px solid rgba(255,255,255,.04);" if i < len(transactions)-1 else ""

        st.markdown(f"""
        <div style="padding:14px 22px;{border}
                    display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;gap:12px;
                    align-items:center;transition:background .15s;"
             onmouseover="this.style.background='rgba(255,255,255,.02)'"
             onmouseout="this.style.background='transparent'">
          <span style="font-family:'Space Mono',monospace;font-size:.62rem;
                       color:rgba(255,255,255,.4);overflow:hidden;text-overflow:ellipsis;">{order_short}</span>
          <span style="font-family:'Syne',sans-serif;font-size:.88rem;
                       color:#F0ECF8;font-weight:700;">{amount}</span>
          <span style="display:inline-flex;align-items:center;justify-content:center;
                       font-family:'Space Mono',monospace;font-size:.52rem;
                       color:{sc};text-transform:uppercase;letter-spacing:.06em;
                       background:{sbg};border:1px solid {sbrd};
                       border-radius:99px;padding:3px 9px;width:fit-content;">{status}</span>
          <span style="font-family:'Outfit',sans-serif;font-size:.78rem;
                       color:rgba(255,255,255,.35);">{image_ref[:16]}</span>
          <span style="font-family:'Space Mono',monospace;font-size:.58rem;
                       color:rgba(255,255,255,.2);">{date}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)