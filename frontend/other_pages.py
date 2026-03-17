"""
frontend/other_pages.py  —  Task 18 (enhanced)
Gallery + Profile with full history, payment status, re-download, ZIP, filtering
"""

import streamlit as st
import sys, os, io, zipfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.auth import get_image_history, update_password
from backend.download_manager import get_download_bytes, get_user_download_history
from backend.payment import get_user_transactions
from utils.styles import back_button
from database.db import get_connection

GRAD = [
    "linear-gradient(135deg,#1A1728,#201630)",
    "linear-gradient(135deg,#0F1A28,#0F2018)",
    "linear-gradient(135deg,#200F18,#1A1014)",
    "linear-gradient(135deg,#1A1420,#0F1428)",
    "linear-gradient(135deg,#201820,#0F1820)",
    "linear-gradient(135deg,#181428,#200F14)",
]


def _mono(text, color="#3E3C58"):
    st.markdown(
        f'<p style="font-family:Syne Mono,monospace;font-size:.58rem;color:{color};'
        f'text-transform:uppercase;letter-spacing:.16em;margin:0 0 8px;">{text}</p>',
        unsafe_allow_html=True,
    )


def _status_badge(status: str) -> str:
    cfg = {
        "paid":         ("#34D399", "rgba(52,211,153,.1)",  "rgba(52,211,153,.25)",  "Paid"),
        "free_preview": ("#FBBF24", "rgba(251,191,36,.1)",  "rgba(251,191,36,.25)",  "Free Preview"),
        "free":         ("#A78BFA", "rgba(167,139,250,.1)", "rgba(167,139,250,.25)", "Free"),
    }
    col, bg, brd, label = cfg.get(status, ("#7C7A9A","rgba(255,255,255,.06)","rgba(255,255,255,.1)","Unknown"))
    return (
        f'<span style="font-family:Syne Mono,monospace;font-size:.55rem;'
        f'background:{bg};border:1px solid {brd};border-radius:99px;'
        f'padding:3px 10px;color:{col};text-transform:uppercase;letter-spacing:.07em;">'
        f'{label}</span>'
    )


# ── GALLERY  (Task 18) ────────────────────────────────────────────────────────

def show_history_page():
    back_button("Back", "dashboard")
    user    = st.session_state.get("user", {})
    uid     = user.get("user_id", 0)
    history = get_user_download_history(uid)

    st.markdown("""
    <div style="margin-bottom:24px;">
      <p style="font-family:'Syne Mono',monospace;font-size:.58rem;color:#3E3C58;
                text-transform:uppercase;letter-spacing:.18em;margin:0 0 8px;">Collection</p>
      <h2 style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
                 color:#EEEAF8;margin:0;letter-spacing:-.04em;">My Gallery</h2>
    </div>
    """, unsafe_allow_html=True)

    if not history:
        st.markdown("""
        <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.06);
                    border-radius:16px;padding:60px;text-align:center;">
          <p style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;
                    color:#3E3C58;margin:0 0 6px;">No artworks yet</p>
          <p style="font-family:'Outfit',sans-serif;font-size:.85rem;color:#3E3C58;margin:0;">
            Head to Art Studio to create your first artwork
          </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("Go to Art Studio", type="primary", key="gal_cta"):
            st.session_state["page"] = "image_processing"
            st.rerun()
        return

    # ── Filter / Sort bar ─────────────────────────────────────────────────────
    from collections import Counter
    all_styles   = list(dict.fromkeys(h.get("style_applied","") for h in history))
    all_statuses = ["All", "paid", "free_preview"]

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

    # ── ZIP download for paid images ──────────────────────────────────────────
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

    # Style pills + item count
    sc    = Counter(h.get("style_applied","") for h in filtered)
    COLS  = ["#A78BFA","#F472B6","#60A5FA","#34D399","#FBBF24","#F87171"]
    pills = "".join([
        f'<span style="font-family:Syne Mono,monospace;font-size:.57rem;letter-spacing:.06em;'
        f'text-transform:uppercase;padding:4px 10px;border-radius:99px;'
        f'background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);'
        f'color:{COLS[i%6]};margin-right:5px;">'
        f'{s.split(" ",1)[-1] if " " in s else s}: {c}</span>'
        for i, (s, c) in enumerate(sc.most_common(8)) if s
    ])
    st.markdown(
        f'<div style="display:flex;flex-wrap:wrap;align-items:center;gap:4px;'
        f'margin:12px 0 20px;">'
        f'<span style="font-family:Syne Mono,monospace;font-size:.56rem;color:#3E3C58;'
        f'letter-spacing:.1em;text-transform:uppercase;margin-right:8px;">{len(filtered)} items</span>'
        f'{pills}</div>',
        unsafe_allow_html=True
    )

    # ── Pagination ────────────────────────────────────────────────────────────
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
                if ppath and os.path.exists(ppath):
                    st.image(ppath, use_container_width=True)
                else:
                    st.markdown(
                        f'<div style="aspect-ratio:.9;border-radius:12px;'
                        f'background:{GRAD[(i+j)%len(GRAD)]};display:flex;'
                        f'align-items:center;justify-content:center;font-size:2rem;'
                        f'border:1px solid rgba(255,255,255,.06);">🖼</div>',
                        unsafe_allow_html=True
                    )
                st.markdown(
                    f'<div style="padding:6px 0 4px;">'
                    f'<p style="font-family:Outfit,sans-serif;font-weight:600;'
                    f'font-size:.78rem;color:#EEEAF8;margin:0 0 4px;">'
                    f'{item.get("style_applied","-")}</p>'
                    f'{_status_badge(status)}'
                    f'<p style="font-family:Syne Mono,monospace;font-size:.56rem;'
                    f'color:#3E3C58;margin:4px 0 0;">'
                    f'{(item.get("processing_date","") or "")[:10]}</p></div>',
                    unsafe_allow_html=True
                )
                # Re-download button for paid images
                if status == "paid":
                    data, fname = get_download_bytes(item["id"], uid, "PNG")
                    if data:
                        st.download_button("⬇ Re-download", data=data,
                                           file_name=fname, mime="image/png",
                                           use_container_width=True,
                                           key=f"redl_{item['id']}")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Pagination controls
    if total_pages > 1:
        p1, p2, p3 = st.columns([1,2,1])
        with p1:
            if st.button("← Prev", disabled=page_num==1, key="gal_prev"):
                st.session_state["gal_page"] = page_num - 1
                st.rerun()
        with p2:
            st.markdown(
                f'<p style="font-family:Syne Mono,monospace;font-size:.65rem;'
                f'color:#3E3C58;text-align:center;margin-top:10px;">'
                f'Page {page_num} / {total_pages}</p>',
                unsafe_allow_html=True
            )
        with p3:
            if st.button("Next →", disabled=page_num==total_pages, key="gal_next"):
                st.session_state["gal_page"] = page_num + 1
                st.rerun()

    # Delete history option
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    with st.expander("⚠️ Delete Processing History"):
        st.markdown("""
        <p style="font-family:'Outfit',sans-serif;font-size:.85rem;color:#F472B6;margin:0 0 10px;">
          This will permanently delete all image records and files from the server.
          Paid images cannot be recovered.
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


# ── PROFILE  (Task 18) ────────────────────────────────────────────────────────

def show_profile_page():
    back_button("Back", "dashboard")
    user    = st.session_state.get("user", {})
    uname   = user.get("username", "-")
    initial = uname[0].upper() if uname else "?"
    uid     = user.get("user_id", 0)
    history = get_image_history(uid)
    txns    = get_user_transactions(uid)

    st.markdown("""
    <div style="margin-bottom:24px;">
      <p style="font-family:'Syne Mono',monospace;font-size:.58rem;color:#3E3C58;
                text-transform:uppercase;letter-spacing:.18em;margin:0 0 8px;">Account</p>
      <h2 style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
                 color:#EEEAF8;margin:0;letter-spacing:-.04em;">Profile</h2>
    </div>
    """, unsafe_allow_html=True)

    avatar_col, details_col = st.columns([1, 2.2])

    # ── Avatar card ───────────────────────────────────────────────────────────
    with avatar_col:
        styles_used  = len(set(h["style_applied"] for h in history)) if history else 0
        paid_count   = sum(1 for h in history if h.get("payment_status") == "paid")
        total_spent  = sum(t.get("amount", 0) for t in txns if t.get("status") == "success")

        st.markdown(f"""
        <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.06);
                    border-radius:18px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.4);">
          <div style="height:80px;background:linear-gradient(135deg,#A78BFA,#F472B6);position:relative;overflow:hidden;">
            <div style="position:absolute;inset:0;background:repeating-linear-gradient(
              45deg,transparent,transparent 10px,rgba(0,0,0,.08) 10px,rgba(0,0,0,.08) 11px);"></div>
          </div>
          <div style="display:flex;justify-content:center;margin-top:-28px;position:relative;z-index:1;">
            <div style="width:56px;height:56px;border-radius:50%;
                        background:linear-gradient(135deg,#A78BFA,#F472B6);
                        display:flex;align-items:center;justify-content:center;
                        font-family:'Syne',sans-serif;font-weight:800;font-size:1.4rem;
                        color:#fff;border:3px solid #08080E;
                        box-shadow:0 0 20px rgba(167,139,250,.3);">{initial}</div>
          </div>
          <div style="padding:12px 20px 24px;text-align:center;">
            <p style="font-family:'Syne',sans-serif;font-weight:700;
                      font-size:1rem;color:#EEEAF8;margin:0 0 8px;">{uname}</p>
            <span style="font-family:'Syne Mono',monospace;font-size:.56rem;
                         letter-spacing:.08em;text-transform:uppercase;padding:4px 12px;
                         border-radius:99px;background:rgba(52,211,153,.06);
                         border:1px solid rgba(52,211,153,.2);color:#34D399;">Free Plan</span>
            <div style="display:flex;justify-content:space-around;
                        margin-top:18px;padding-top:16px;border-top:1px solid rgba(255,255,255,.05);">
              <div style="text-align:center;">
                <p style="font-family:'Syne',sans-serif;font-weight:800;
                           font-size:1.4rem;color:#EEEAF8;margin:0;">{len(history)}</p>
                <p style="font-family:'Syne Mono',monospace;font-size:.55rem;color:#3E3C58;
                           text-transform:uppercase;letter-spacing:.07em;margin:2px 0 0;">Images</p>
              </div>
              <div style="width:1px;background:rgba(255,255,255,.05);"></div>
              <div style="text-align:center;">
                <p style="font-family:'Syne',sans-serif;font-weight:800;
                           font-size:1.4rem;color:#EEEAF8;margin:0;">{styles_used}</p>
                <p style="font-family:'Syne Mono',monospace;font-size:.55rem;color:#3E3C58;
                           text-transform:uppercase;letter-spacing:.07em;margin:2px 0 0;">Styles</p>
              </div>
              <div style="width:1px;background:rgba(255,255,255,.05);"></div>
              <div style="text-align:center;">
                <p style="font-family:'Syne',sans-serif;font-weight:800;
                           font-size:1.4rem;color:#A78BFA;margin:0;">₹{total_spent:.0f}</p>
                <p style="font-family:'Syne Mono',monospace;font-size:.55rem;color:#A78BFA;
                           text-transform:uppercase;letter-spacing:.07em;margin:2px 0 0;">Spent</p>
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Details + tabs ────────────────────────────────────────────────────────
    with details_col:
        tab1, tab2, tab3 = st.tabs(["Account Details", "Payment History", "Security"])

        with tab1:
            fields = [
                ("Username",     user.get("username",  "-")),
                ("Email",        user.get("email",     "-")),
                ("Member Since", (user.get("created_at","") or "")[:10] or "-"),
                ("Last Login",   (user.get("last_login","") or "First visit")[:16]),
                ("Total Images", str(len(history))),
                ("Paid Downloads", str(paid_count)),
                ("Favourite Style", (
                    max(set(h["style_applied"] for h in history),
                        key=lambda s: sum(1 for h in history if h["style_applied"]==s))
                    if history else "-"
                )),
            ]
            rows_html = "".join([
                f'<div style="{"border-bottom:1px solid rgba(255,255,255,.04);" if i<len(fields)-1 else ""}padding:12px 18px;">'
                f'<p style="font-family:Syne Mono,monospace;font-size:.55rem;color:#3E3C58;'
                f'text-transform:uppercase;letter-spacing:.1em;margin:0 0 3px;">{lbl}</p>'
                f'<p style="font-family:Outfit,sans-serif;font-weight:600;'
                f'font-size:.88rem;color:#EEEAF8;margin:0;">{val}</p></div>'
                for i, (lbl, val) in enumerate(fields)
            ])
            st.markdown(f"""
            <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.06);
                        border-radius:14px;overflow:hidden;">
              {rows_html}
            </div>
            """, unsafe_allow_html=True)

        with tab2:
            if not txns:
                st.markdown("""
                <div style="padding:40px;text-align:center;background:#0F0F18;
                            border:1px solid rgba(255,255,255,.06);border-radius:14px;">
                  <p style="font-family:Outfit,sans-serif;color:#3E3C58;margin:0;">
                    No transactions yet
                  </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                for tx in txns[:15]:
                    status = tx.get("status","pending")
                    s_color = {"success":"#34D399","pending":"#FBBF24","failed":"#F472B6"}.get(status,"#7C7A9A")
                    st.markdown(f"""
                    <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.06);
                                border-radius:12px;padding:12px 16px;margin-bottom:8px;
                                display:flex;justify-content:space-between;align-items:center;">
                      <div>
                        <p style="font-family:'Syne Mono',monospace;font-size:.62rem;
                                  color:#EEEAF8;margin:0 0 3px;">
                          {(tx.get('razorpay_payment_id') or tx.get('razorpay_order_id') or f"TX-{tx.get('id','—')}")[:24]}
                        </p>
                        <p style="font-family:'Outfit',sans-serif;font-size:.78rem;
                                  color:#7C7A9A;margin:0;">{tx.get('created_at','')[:16]}</p>
                      </div>
                      <div style="text-align:right;">
                        <p style="font-family:'Syne',sans-serif;font-weight:700;
                                  font-size:.88rem;color:#EEEAF8;margin:0 0 3px;">
                          ₹{tx.get('amount',10.0):.2f}
                        </p>
                        <span style="font-family:Syne Mono,monospace;font-size:.55rem;
                                     color:{s_color};text-transform:uppercase;letter-spacing:.06em;">
                          {status}
                        </span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

        with tab3:
            st.markdown("""
            <p style="font-family:'Syne Mono',monospace;font-size:.58rem;color:#3E3C58;
                      text-transform:uppercase;letter-spacing:.1em;margin:0 0 14px;">
              Change Password
            </p>
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

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

            # Danger zone
            st.markdown("""
            <div style="background:rgba(244,114,182,.04);border:1px solid rgba(244,114,182,.1);
                        border-radius:12px;padding:16px 20px;">
              <p style="font-family:'Syne Mono',monospace;font-size:.56rem;
                        color:rgba(244,114,182,.5);text-transform:uppercase;
                        letter-spacing:.1em;margin:0 0 10px;">Danger Zone</p>
              <p style="font-family:'Outfit',sans-serif;font-size:.82rem;
                        color:#7C7A9A;margin:0 0 12px;">
                Deleting your account will remove all data and is irreversible.
              </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
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
