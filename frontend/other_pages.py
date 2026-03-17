"""
frontend/other_pages.py — Gallery + Profile with upgraded UI
"""

import streamlit as st
import sys, os, io, zipfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.auth import get_image_history, update_password
from backend.download_manager import get_download_bytes, get_user_download_history
from payment.razorpay_handler import get_user_transactions
from database.db import get_connection

try:
    from utils.styles import back_button
except ImportError:
    def back_button(label, page):
        if st.button(f"← {label}", key="back_nav"):
            st.session_state["page"] = page
            st.rerun()

GRAD = [
    "linear-gradient(135deg,#1A1728,#201630)",
    "linear-gradient(135deg,#0F1A28,#0F2018)",
    "linear-gradient(135deg,#200F18,#1A1014)",
    "linear-gradient(135deg,#1A1420,#0F1428)",
    "linear-gradient(135deg,#201820,#0F1820)",
    "linear-gradient(135deg,#181428,#200F14)",
]


def _page_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Outfit:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

    html, body, .stApp { background:#06060E !important; }
    #MainMenu, footer, header[data-testid="stHeader"],
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] { display:none !important; }
    .block-container { padding: 24px 32px 48px !important; max-width: 1300px !important; }

    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,.025) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        border: 1px solid rgba(255,255,255,.06) !important;
        gap: 4px !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important;
        font-size: .85rem !important;
        color: rgba(255,255,255,.4) !important;
        padding: 8px 18px !important;
        transition: all .18s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(147,112,219,.15) !important;
        color: #C471ED !important;
    }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 20px !important; }

    .stSelectbox > div > div {
        background: rgba(255,255,255,.03) !important;
        border: 1px solid rgba(255,255,255,.08) !important;
        border-radius: 12px !important;
        color: #F0ECF8 !important;
        font-family: 'Outfit', sans-serif !important;
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

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg,#9370DB,#C471ED) !important;
        color: #fff !important; border: none !important;
        border-radius: 12px !important; height: 44px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important; font-size: .85rem !important;
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
        border-radius: 12px !important; height: 44px !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: .83rem !important; transition: all .18s ease !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        border-color: rgba(147,112,219,.3) !important;
        color: #C471ED !important;
        background: rgba(147,112,219,.05) !important;
        transform: translateY(-1px) !important;
    }
    .stDownloadButton > button {
        background: rgba(52,211,153,.06) !important;
        border: 1px solid rgba(52,211,153,.18) !important;
        color: #34D399 !important;
        border-radius: 10px !important; height: 40px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important; font-size: .8rem !important;
        transition: all .18s ease !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(52,211,153,.1) !important;
        transform: translateY(-1px) !important;
    }
    .stExpander {
        background: rgba(255,255,255,.02) !important;
        border: 1px solid rgba(255,255,255,.06) !important;
        border-radius: 14px !important;
    }
    .stExpander summary {
        font-family: 'Outfit', sans-serif !important;
        color: rgba(255,255,255,.5) !important;
    }
    .stCheckbox label span {
        font-family: 'Outfit', sans-serif !important;
        color: rgba(255,255,255,.4) !important;
        font-size: .85rem !important;
    }
    </style>
    """, unsafe_allow_html=True)


def _status_badge(status: str) -> str:
    cfg = {
        "paid":         ("#34D399", "rgba(52,211,153,.08)",  "rgba(52,211,153,.2)",  "Paid"),
        "free_preview": ("#FBBF24", "rgba(251,191,36,.08)",  "rgba(251,191,36,.2)",  "Preview"),
        "free":         ("#9370DB", "rgba(147,112,219,.08)", "rgba(147,112,219,.2)", "Free"),
    }
    col, bg, brd, label = cfg.get(status, ("#7C7A9A","rgba(255,255,255,.05)","rgba(255,255,255,.1)","Unknown"))
    return (
        f'<span style="font-family:Space Mono,monospace;font-size:.54rem;'
        f'background:{bg};border:1px solid {brd};border-radius:99px;'
        f'padding:3px 9px;color:{col};text-transform:uppercase;letter-spacing:.07em;">'
        f'{label}</span>'
    )


# ── GALLERY ───────────────────────────────────────────────────────────────────

def show_history_page():
    _page_styles()
    back_button("Back", "dashboard")
    user    = st.session_state.get("user", {})
    uid     = user.get("user_id", 0)
    history = get_user_download_history(uid)

    st.markdown("""
    <div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid rgba(255,255,255,.05);">
      <p style="font-family:'Space Mono',monospace;font-size:.6rem;color:rgba(147,112,219,.6);
                text-transform:uppercase;letter-spacing:.18em;margin:0 0 8px;">Collection</p>
      <h2 style="font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;
                 color:#F0ECF8;margin:0;letter-spacing:-.05em;">My Gallery</h2>
    </div>
    """, unsafe_allow_html=True)

    if not history:
        st.markdown("""
        <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.06);
                    border-radius:20px;padding:70px;text-align:center;">
          <div style="font-size:3rem;margin-bottom:18px;opacity:.25;">🖼️</div>
          <p style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;
                    color:rgba(255,255,255,.25);margin:0 0 8px;">No artworks yet</p>
          <p style="font-family:'Outfit',sans-serif;font-size:.85rem;
                    color:rgba(255,255,255,.18);margin:0 0 24px;">
            Head to Art Studio to create your first artwork
          </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        if st.button("Go to Art Studio 🎨", type="primary", key="gal_cta"):
            st.session_state["page"] = "image_processing"
            st.rerun()
        return

    # Filter bar
    from collections import Counter
    all_styles   = list(dict.fromkeys(h.get("style_applied","") for h in history))
    all_statuses = ["All", "paid", "free_preview"]

    st.markdown("""
    <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.06);
                border-radius:14px;padding:16px 20px;margin-bottom:20px;">
      <p style="font-family:'Space Mono',monospace;font-size:.58rem;color:rgba(255,255,255,.2);
                text-transform:uppercase;letter-spacing:.12em;margin:0 0 12px;">Filter & Sort</p>
    </div>
    """, unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns([2, 1.5, 1.5])
    with fc1:
        style_filter = st.selectbox("Filter by Style", ["All"] + all_styles,
                                    key="gal_style_f", label_visibility="collapsed")
    with fc2:
        status_filter = st.selectbox("Filter by Status", all_statuses,
                                     key="gal_status_f", label_visibility="collapsed")
    with fc3:
        sort_by = st.selectbox("Sort", ["Newest", "Oldest", "Style"],
                               key="gal_sort", label_visibility="collapsed")

    filtered = [h for h in history
                if (style_filter  == "All" or h.get("style_applied") == style_filter)
                and (status_filter == "All" or h.get("payment_status") == status_filter)]
    if sort_by == "Oldest":
        filtered = list(reversed(filtered))
    elif sort_by == "Style":
        filtered = sorted(filtered, key=lambda x: x.get("style_applied",""))

    # ZIP for paid
    paid = [h for h in filtered if h.get("payment_status") == "paid"]
    if paid:
        if st.button(f"⬇ Download All Paid ({len(paid)}) as ZIP",
                     use_container_width=True, key="zip_all"):
            zbuf = io.BytesIO()
            with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as zf:
                for item in paid:
                    data, fname = get_download_bytes(item["id"], uid, "PNG")
                    if data:
                        zf.writestr(fname, data)
            zbuf.seek(0)
            st.download_button(
                "Click to Save ZIP",
                data=zbuf.getvalue(),
                file_name="cartoonize_artworks.zip",
                mime="application/zip",
                key="zip_dl"
            )

    # Style pills
    sc    = Counter(h.get("style_applied","") for h in filtered)
    COLS  = ["#9370DB","#C471ED","#60A5FA","#34D399","#FBBF24","#F87171"]
    pills = "".join([
        f'<span style="font-family:Space Mono,monospace;font-size:.55rem;'
        f'letter-spacing:.06em;text-transform:uppercase;padding:3px 10px;border-radius:99px;'
        f'background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);'
        f'color:{COLS[i%6]};margin-right:5px;">'
        f'{s.split(" ",1)[-1] if " " in s else s}: {c}</span>'
        for i, (s, c) in enumerate(sc.most_common(8)) if s
    ])
    st.markdown(
        f'<div style="display:flex;flex-wrap:wrap;align-items:center;gap:4px;'
        f'margin:14px 0 22px;">'
        f'<span style="font-family:Space Mono,monospace;font-size:.56rem;color:rgba(255,255,255,.2);'
        f'letter-spacing:.1em;text-transform:uppercase;margin-right:10px;">{len(filtered)} items</span>'
        f'{pills}</div>',
        unsafe_allow_html=True
    )

    # Pagination
    PAGE_SIZE = 8
    total_pages = max(1, (len(filtered) + PAGE_SIZE - 1) // PAGE_SIZE)
    page_num    = st.session_state.get("gal_page", 1)
    page_num    = max(1, min(page_num, total_pages))
    batch       = filtered[(page_num-1)*PAGE_SIZE : page_num*PAGE_SIZE]

    CPR = 4
    for i in range(0, len(batch), CPR):
        chunk = batch[i:i+CPR]
        cols  = st.columns(CPR)
        for j, (col, item) in enumerate(zip(cols, chunk)):
            with col:
                ppath  = item.get("processed_image_path","")
                status = item.get("payment_status","free_preview")

                # Image
                st.markdown("""
                <div style="border-radius:14px;overflow:hidden;
                            border:1px solid rgba(255,255,255,.06);
                            box-shadow:0 4px 16px rgba(0,0,0,.4);">
                """, unsafe_allow_html=True)
                if ppath and os.path.exists(ppath):
                    st.image(ppath, use_container_width=True)
                else:
                    st.markdown(
                        f'<div style="aspect-ratio:.9;border-radius:14px;'
                        f'background:{GRAD[(i+j)%len(GRAD)]};display:flex;'
                        f'align-items:center;justify-content:center;font-size:2rem;">🖼</div>',
                        unsafe_allow_html=True
                    )
                st.markdown("</div>", unsafe_allow_html=True)

                # Metadata
                style_name = item.get("style_applied","-")
                short_style = style_name.split(" ", 1)[-1] if " " in style_name else style_name
                date  = (item.get("processing_date","") or "")[:10]
                st.markdown(
                    f'<div style="padding:8px 0 4px;">'
                    f'<p style="font-family:Outfit,sans-serif;font-weight:600;'
                    f'font-size:.78rem;color:#F0ECF8;margin:0 0 5px;">{short_style}</p>'
                    f'{_status_badge(status)}'
                    f'<p style="font-family:Space Mono,monospace;font-size:.54rem;'
                    f'color:rgba(255,255,255,.2);margin:5px 0 0;">{date}</p></div>',
                    unsafe_allow_html=True
                )
                if status == "paid":
                    data, fname = get_download_bytes(item["id"], uid, "PNG")
                    if data:
                        st.download_button("⬇ Re-download", data=data,
                                           file_name=fname, mime="image/png",
                                           use_container_width=True,
                                           key=f"redl_{item['id']}")
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # Pagination controls
    if total_pages > 1:
        p1, p2, p3 = st.columns([1,2,1])
        with p1:
            if st.button("← Prev", disabled=page_num==1, key="gal_prev"):
                st.session_state["gal_page"] = page_num - 1
                st.rerun()
        with p2:
            st.markdown(
                f'<p style="font-family:Space Mono,monospace;font-size:.64rem;'
                f'color:rgba(255,255,255,.25);text-align:center;margin-top:11px;">'
                f'Page {page_num} / {total_pages}</p>',
                unsafe_allow_html=True
            )
        with p3:
            if st.button("Next →", disabled=page_num==total_pages, key="gal_next"):
                st.session_state["gal_page"] = page_num + 1
                st.rerun()

    # Delete history
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    with st.expander("⚠️ Delete Processing History"):
        st.markdown("""
        <p style="font-family:'Outfit',sans-serif;font-size:.85rem;
                  color:rgba(246,79,89,.7);margin:0 0 12px;">
          This will permanently delete all image records and files from the server.
        </p>
        """, unsafe_allow_html=True)
        if st.button("Delete All History", key="del_hist_btn"):
            conn = get_connection()
            rows = conn.execute(
                "SELECT processed_image_path, watermarked_path, original_image_path FROM image_history WHERE user_id=?",
                (uid,)
            ).fetchall()
            for r in rows:
                for path in [r["processed_image_path"], r["watermarked_path"], r["original_image_path"]]:
                    if path and os.path.exists(path):
                        try: os.remove(path)
                        except: pass
            conn.execute("DELETE FROM image_history WHERE user_id=?", (uid,))
            conn.execute("DELETE FROM download_logs WHERE user_id=?", (uid,))
            conn.commit()
            conn.close()
            st.success("History cleared.")
            st.rerun()


# ── PROFILE ───────────────────────────────────────────────────────────────────

def show_profile_page():
    _page_styles()
    back_button("Back", "dashboard")
    user    = st.session_state.get("user", {})
    uname   = user.get("username", "-")
    initial = uname[0].upper() if uname else "?"
    uid     = user.get("user_id", 0)
    history = get_image_history(uid)
    txns    = get_user_transactions(uid)

    st.markdown("""
    <div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid rgba(255,255,255,.05);">
      <p style="font-family:'Space Mono',monospace;font-size:.6rem;color:rgba(147,112,219,.6);
                text-transform:uppercase;letter-spacing:.18em;margin:0 0 8px;">Account</p>
      <h2 style="font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;
                 color:#F0ECF8;margin:0;letter-spacing:-.05em;">Profile</h2>
    </div>
    """, unsafe_allow_html=True)

    avatar_col, details_col = st.columns([1, 2.2])

    with avatar_col:
        styles_used  = len(set(h["style_applied"] for h in history)) if history else 0
        paid_count   = sum(1 for h in history if h.get("payment_status") == "paid")
        total_spent  = sum(t.get("amount", 0) for t in txns if t.get("status") in ("success","paid"))

        # Banner
        st.markdown("""
        <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.06);
                    border-radius:20px 20px 0 0;overflow:hidden;box-shadow:0 4px 0 rgba(0,0,0,.2);">
          <div style="height:90px;background:linear-gradient(135deg,#9370DB,#C471ED,#F64F59);
                      position:relative;overflow:hidden;">
            <div style="position:absolute;inset:0;
                        background:repeating-linear-gradient(45deg,transparent,transparent 12px,
                                   rgba(0,0,0,.06) 12px,rgba(0,0,0,.06) 13px);"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Avatar + name + plan badge
        st.markdown(f"""
        <div style="background:#0A0A14;border-left:1px solid rgba(255,255,255,.06);
                    border-right:1px solid rgba(255,255,255,.06);
                    padding:0 20px 16px;text-align:center;margin-top:-2px;">
          <div style="display:flex;justify-content:center;margin-top:-30px;margin-bottom:10px;">
            <div style="width:60px;height:60px;border-radius:50%;
                        background:linear-gradient(135deg,#9370DB,#C471ED);
                        display:flex;align-items:center;justify-content:center;
                        font-family:'Syne',sans-serif;font-weight:800;font-size:1.5rem;
                        color:#fff;border:3px solid #06060E;
                        box-shadow:0 0 24px rgba(147,112,219,.4);">{initial}</div>
          </div>
          <p style="font-family:'Syne',sans-serif;font-weight:700;
                    font-size:1.05rem;color:#F0ECF8;margin:0 0 10px;">{uname}</p>
          <span style="font-family:'Space Mono',monospace;font-size:.55rem;
                       letter-spacing:.1em;text-transform:uppercase;padding:4px 12px;
                       border-radius:99px;background:rgba(52,211,153,.06);
                       border:1px solid rgba(52,211,153,.18);color:#34D399;">Free Plan</span>
        </div>
        """, unsafe_allow_html=True)

        # Stats row — using st.columns so values always render
        st.markdown("""
        <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.06);
                    border-top:1px solid rgba(255,255,255,.05);border-radius:0 0 20px 20px;
                    padding:16px 4px 20px;margin-top:-2px;box-shadow:0 8px 32px rgba(0,0,0,.4);">
        </div>
        """, unsafe_allow_html=True)

        sc1, sc2, sc3 = st.columns(3)
        for col, val, lbl, color in [
            (sc1, len(history),       "Artworks", "#F0ECF8"),
            (sc2, styles_used,        "Styles",   "#F0ECF8"),
            (sc3, f"₹{int(total_spent)}", "Spent", "#9370DB"),
        ]:
            with col:
                st.markdown(f"""
                <div style="text-align:center;padding:4px 0 8px;">
                  <p style="font-family:'Syne',sans-serif;font-weight:800;
                             font-size:1.5rem;color:{color};margin:0;">{val}</p>
                  <p style="font-family:'Space Mono',monospace;font-size:.52rem;
                             color:rgba(255,255,255,.25);text-transform:uppercase;
                             letter-spacing:.07em;margin:4px 0 0;">{lbl}</p>
                </div>
                """, unsafe_allow_html=True)

    with details_col:
        tab1, tab2, tab3 = st.tabs(["Account Details", "Payment History", "Security"])

        with tab1:
            fields = [
                ("Username",       user.get("username",  "-")),
                ("Email",          user.get("email",     "-")),
                ("Member Since",   (user.get("created_at","") or "")[:10] or "-"),
                ("Last Login",     (user.get("last_login","") or "First visit")[:16]),
                ("Total Images",   str(len(history))),
                ("Paid Downloads", str(paid_count)),
                ("Favourite Style", (
                    max(set(h["style_applied"] for h in history),
                        key=lambda s: sum(1 for h in history if h["style_applied"]==s))
                    if history else "-"
                )),
            ]
            def _field_row(i, lbl, val, total):
                border = "border-bottom:1px solid rgba(255,255,255,.04);" if i < total - 1 else ""
                return (
                    f'<div style="{border}padding:13px 20px;">'
                    f'<p style="font-family:Space Mono,monospace;font-size:.55rem;color:rgba(255,255,255,.25);'
                    f'text-transform:uppercase;letter-spacing:.1em;margin:0 0 3px;">{lbl}</p>'
                    f'<p style="font-family:Outfit,sans-serif;font-weight:600;'
                    f'font-size:.88rem;color:#F0ECF8;margin:0;">{val}</p></div>'
                )
            rows_html = "".join([
                _field_row(i, lbl, val, len(fields))
                for i, (lbl, val) in enumerate(fields)
            ])
            st.markdown(f"""
            <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.06);
                        border-radius:16px;overflow:hidden;">
              {rows_html}
            </div>
            """, unsafe_allow_html=True)

        with tab2:
            if not txns:
                st.markdown("""
                <div style="padding:50px;text-align:center;background:#0A0A14;
                            border:1px solid rgba(255,255,255,.06);border-radius:16px;">
                  <div style="font-size:2rem;opacity:.2;margin-bottom:12px;">💳</div>
                  <p style="font-family:Outfit,sans-serif;color:rgba(255,255,255,.25);margin:0;">
                    No transactions yet
                  </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                for tx in txns[:15]:
                    status = tx.get("status","pending")
                    s_color = {"success":"#34D399","paid":"#34D399","pending":"#FBBF24","failed":"#F64F59"}.get(status,"#7C7A9A")
                    s_bg    = {"success":"rgba(52,211,153,.06)","paid":"rgba(52,211,153,.06)","pending":"rgba(251,191,36,.06)","failed":"rgba(246,79,89,.06)"}.get(status,"rgba(255,255,255,.03)")
                    s_brd   = {"success":"rgba(52,211,153,.15)","paid":"rgba(52,211,153,.15)","pending":"rgba(251,191,36,.15)","failed":"rgba(246,79,89,.15)"}.get(status,"rgba(255,255,255,.06)")
                    tx_id   = (tx.get('razorpay_payment_id') or tx.get('razorpay_order_id') or f"TX-{tx.get('id','—')}")[:24]
                    st.markdown(f"""
                    <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.06);
                                border-radius:14px;padding:14px 18px;margin-bottom:8px;
                                display:flex;justify-content:space-between;align-items:center;">
                      <div>
                        <p style="font-family:'Space Mono',monospace;font-size:.62rem;
                                  color:#F0ECF8;margin:0 0 4px;">{tx_id}</p>
                        <p style="font-family:'Outfit',sans-serif;font-size:.77rem;
                                  color:rgba(255,255,255,.25);margin:0;">{tx.get('created_at','')[:16]}</p>
                      </div>
                      <div style="text-align:right;">
                        <p style="font-family:'Syne',sans-serif;font-weight:700;
                                  font-size:.9rem;color:#F0ECF8;margin:0 0 4px;">
                          ₹{tx.get('amount',10.0):.0f}
                        </p>
                        <span style="font-family:Space Mono,monospace;font-size:.54rem;
                                     background:{s_bg};border:1px solid {s_brd};
                                     border-radius:99px;padding:2px 8px;
                                     color:{s_color};text-transform:uppercase;letter-spacing:.06em;">
                          {status}
                        </span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

        with tab3:
            st.markdown("""
            <p style="font-family:'Space Mono',monospace;font-size:.6rem;
                      color:rgba(255,255,255,.25);text-transform:uppercase;
                      letter-spacing:.12em;margin:0 0 16px;">Change Password</p>
            """, unsafe_allow_html=True)

            cur_pw  = st.text_input("Current Password", type="password", key="cur_pw")
            new_pw  = st.text_input("New Password",     type="password", key="new_pw")
            conf_pw = st.text_input("Confirm New",      type="password", key="conf_pw")

            if st.button("Update Password", type="primary", key="chpw_btn"):
                if not cur_pw or not new_pw or not conf_pw:
                    st.error("Please fill in all fields.")
                elif new_pw != conf_pw:
                    st.error("New passwords do not match.")
                elif len(new_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    from backend.auth import login_user
                    check = login_user(user.get("email",""), cur_pw)
                    if not check["success"]:
                        check = login_user(user.get("username",""), cur_pw)
                    if check["success"]:
                        res = update_password(uid, new_pw)
                        st.success(res["message"])
                    else:
                        st.error("Current password is incorrect.")

            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

            # Danger zone
            st.markdown("""
            <div style="background:rgba(246,79,89,.04);border:1px solid rgba(246,79,89,.1);
                        border-radius:14px;padding:18px 20px;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <span style="font-size:.9rem;">⚠️</span>
                <p style="font-family:'Space Mono',monospace;font-size:.56rem;
                          color:rgba(246,79,89,.5);text-transform:uppercase;
                          letter-spacing:.1em;margin:0;">Danger Zone</p>
              </div>
              <p style="font-family:'Outfit',sans-serif;font-size:.82rem;
                        color:rgba(255,255,255,.3);margin:0;">
                Deleting your account will remove all data permanently and cannot be undone.
              </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            confirm_del = st.checkbox("I understand this is permanent", key="del_confirm")
            if st.button("Delete Account", disabled=not confirm_del, key="del_btn"):
                conn = get_connection()
                for path_row in conn.execute(
                    "SELECT processed_image_path, watermarked_path FROM image_history WHERE user_id=?", (uid,)
                ).fetchall():
                    for p in [path_row[0], path_row[1]]:
                        if p and os.path.exists(p):
                            try: os.remove(p)
                            except: pass
                conn.execute("DELETE FROM download_logs  WHERE user_id=?", (uid,))
                conn.execute("DELETE FROM Transactions   WHERE user_id=?", (uid,))
                conn.execute("DELETE FROM image_history  WHERE user_id=?", (uid,))
                conn.execute("DELETE FROM users          WHERE user_id=?", (uid,))
                conn.commit()
                conn.close()
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()