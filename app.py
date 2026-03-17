import streamlit as st
import sys, os

ROOT = os.path.dirname(__file__)
sys.path.insert(0, ROOT)

from database.db import init_db
from utils.styles import GLOBAL_CSS
from frontend.login_page import show_login_page
from frontend.register_page import show_register_page
from frontend.dashboard_page import show_dashboard
from frontend.image_processing_page import show_image_processing
from frontend.other_pages import show_history_page, show_profile_page
from frontend.payment_page import (
    show_payment_page,
    show_payment_success,
    show_payment_failure,
    show_payment_history,
)

st.set_page_config(
    page_title="CartoonizeMe",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
init_db()

for k, v in [("logged_in", False), ("page", "login")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Auth pages ───────────────────────────────────────────────────────────────
if not st.session_state["logged_in"]:
    if st.session_state["page"] == "register":
        show_register_page()
    else:
        show_login_page()
    st.stop()

# ── App ──────────────────────────────────────────────────────────────────────
user  = st.session_state.get("user", {})
uname = user.get("username", "User")
page  = st.session_state.get("page", "dashboard")

# Hide sidebar on payment-flow pages for focus
_HIDE_SIDEBAR_PAGES = {"payment_success", "payment_failure"}

if page not in _HIDE_SIDEBAR_PAGES:
    with st.sidebar:

        # Brand
        st.markdown("""
        <div style="padding:22px 16px 18px;border-bottom:1px solid rgba(255,255,255,.05);
                    margin-bottom:14px;">
          <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:36px;height:36px;border-radius:10px;
                        background:linear-gradient(135deg,#A78BFA,#F472B6);
                        display:flex;align-items:center;justify-content:center;
                        flex-shrink:0;box-shadow:0 0 20px rgba(167,139,250,.3);">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                      stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div>
              <p style="font-family:'Syne',sans-serif;font-weight:800;font-size:.9rem;
                        color:#EEEAF8;margin:0;letter-spacing:-.02em;">CartoonizeMe</p>
              <p style="font-family:'Syne Mono',monospace;font-size:.52rem;color:#3E3C58;
                        margin:0;letter-spacing:.1em;text-transform:uppercase;">AI Art Studio</p>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # User card
        initial = uname[0].upper() if uname else "?"
        st.markdown(f"""
        <div style="background:#171723;border:1px solid rgba(255,255,255,.06);
                    border-radius:12px;padding:10px 12px;margin-bottom:18px;">
          <div style="display:flex;align-items:center;gap:9px;">
            <div style="width:32px;height:32px;border-radius:50%;
                        background:linear-gradient(135deg,#A78BFA,#F472B6);
                        display:flex;align-items:center;justify-content:center;
                        font-family:'Syne',sans-serif;font-weight:800;
                        color:#fff;font-size:.82rem;flex-shrink:0;">{initial}</div>
            <div style="min-width:0;">
              <p style="font-family:'Outfit',sans-serif;font-weight:700;font-size:.84rem;
                        color:#EEEAF8;margin:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{uname}</p>
              <p style="font-family:'Syne Mono',monospace;font-size:.52rem;color:#3E3C58;
                        margin:0;text-transform:uppercase;letter-spacing:.06em;">Free Plan</p>
            </div>
            <div style="margin-left:auto;width:7px;height:7px;border-radius:50%;
                        background:#34D399;box-shadow:0 0 8px rgba(52,211,153,.5);flex-shrink:0;"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Nav label
        st.markdown("""
        <p style="font-family:'Syne Mono',monospace;font-size:.54rem;color:#3E3C58;
                  text-transform:uppercase;letter-spacing:.16em;margin:0 0 5px 6px;">Menu</p>
        """, unsafe_allow_html=True)

        nav_items = [
            ("Dashboard",        "dashboard",         "M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"),
            ("Art Studio",       "image_processing",  "M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"),
            ("Gallery",          "history",           "M4 6h16M4 10h16M4 14h16M4 18h16"),
            ("Payment History",  "payment_history",   "M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"),
            ("Profile",          "profile",           "M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8z"),
        ]

        for label, key, icon_d in nav_items:
            active = (page == key)
            if active:
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,rgba(167,139,250,.12),rgba(244,114,182,.06));
                            border:1px solid rgba(167,139,250,.2);border-radius:10px;
                            padding:9px 13px;margin:2px 0;
                            display:flex;align-items:center;gap:9px;">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" style="flex-shrink:0;">
                    <path d="{icon_d}" stroke="#A78BFA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span style="font-family:'Outfit',sans-serif;color:#A78BFA;
                               font-size:.84rem;font-weight:700;">{label}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                if st.button(f"{label}", key=f"nav_{key}", use_container_width=True):
                    st.session_state["page"] = key
                    st.rerun()

        # Stats card
        from backend.auth import get_image_history
        hist        = get_image_history(user.get("user_id", 0))
        styles_used = len(set(h["style_applied"] for h in hist)) if hist else 0

        # Payment summary in sidebar
        try:
            from payment.razorpay_handler import get_user_transactions
            txs        = get_user_transactions(user.get("user_id", 0))
            paid_count = sum(1 for t in txs if t.get("status") == "paid")
        except Exception:
            paid_count = 0

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        pct = min(int(len(hist) / 50 * 100), 100)
        st.markdown(f"""
        <div style="background:#171723;border:1px solid rgba(255,255,255,.06);
                    border-radius:14px;padding:14px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-family:'Syne Mono',monospace;font-size:.54rem;color:#3E3C58;
                         text-transform:uppercase;letter-spacing:.08em;">Storage</span>
            <span style="font-family:'Syne Mono',monospace;font-size:.6rem;color:#A78BFA;">{pct}%</span>
          </div>
          <div style="background:rgba(255,255,255,.06);border-radius:99px;height:3px;overflow:hidden;">
            <div style="height:100%;width:{pct}%;
                        background:linear-gradient(90deg,#A78BFA,#F472B6);
                        border-radius:99px;"></div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;margin-top:14px;gap:4px;">
            <div style="text-align:center;">
              <p style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.05rem;color:#EEEAF8;margin:0;">{len(hist)}</p>
              <p style="font-family:'Syne Mono',monospace;font-size:.46rem;color:#3E3C58;text-transform:uppercase;letter-spacing:.04em;margin:1px 0 0;">Images</p>
            </div>
            <div style="width:1px;background:rgba(255,255,255,.05);"></div>
            <div style="text-align:center;">
              <p style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.05rem;color:#EEEAF8;margin:0;">10</p>
              <p style="font-family:'Syne Mono',monospace;font-size:.46rem;color:#3E3C58;text-transform:uppercase;letter-spacing:.04em;margin:1px 0 0;">Effects</p>
            </div>
            <div style="text-align:center;">
              <p style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.05rem;color:#34D399;margin:0;">{paid_count}</p>
              <p style="font-family:'Syne Mono',monospace;font-size:.46rem;color:#34D399;text-transform:uppercase;letter-spacing:.04em;margin:1px 0 0;">Paid</p>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        if st.button("Sign Out", use_container_width=True, key="logout_btn"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# ── Routing ──────────────────────────────────────────────────────────────────
page = st.session_state.get("page", "dashboard")

if   page == "dashboard":        show_dashboard()
elif page == "image_processing": show_image_processing()
elif page == "history":          show_history_page()
elif page == "profile":          show_profile_page()
elif page == "payment":          show_payment_page()
elif page == "payment_success":  show_payment_success()
elif page == "payment_failure":  show_payment_failure()
elif page == "payment_history":  show_payment_history()
else:                            show_dashboard()