import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.auth import get_image_history
from database.db import get_connection


def show_dashboard():
    user    = st.session_state.get("user", {})
    uname   = user.get("username", "User")
    history = get_image_history(user.get("user_id", 0))

    conn = get_connection()
    tx_count = conn.execute(
        "SELECT COUNT(*) FROM Transactions WHERE user_id=?",
        (user.get("user_id", 0),)
    ).fetchone()[0]
    conn.close()

    member_since = (user.get("created_at", "") or "")[:10] or "-"
    styles_used  = len(set(h["style_applied"] for h in history)) if history else 0

    # ── Ticker ──────────────────────────────────────────────────────────────
    effects = ("CLASSIC CARTOON &nbsp;&nbsp;/&nbsp;&nbsp; WATERCOLOR &nbsp;&nbsp;/&nbsp;&nbsp; "
               "NEON GLOW &nbsp;&nbsp;/&nbsp;&nbsp; ANIME &nbsp;&nbsp;/&nbsp;&nbsp; "
               "PENCIL SKETCH &nbsp;&nbsp;/&nbsp;&nbsp; OIL PAINT &nbsp;&nbsp;/&nbsp;&nbsp; "
               "VINTAGE &nbsp;&nbsp;/&nbsp;&nbsp; PIXEL ART &nbsp;&nbsp;/&nbsp;&nbsp; "
               "COMIC &nbsp;&nbsp;/&nbsp;&nbsp; COLOR PENCIL &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
    st.markdown(f"""
    <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.05);border-radius:12px;
                padding:10px 0;margin-bottom:24px;overflow:hidden;position:relative;">
      <div style="position:absolute;left:0;top:0;bottom:0;width:48px;
                  background:linear-gradient(90deg,#0F0F18,transparent);z-index:2;"></div>
      <div style="position:absolute;right:0;top:0;bottom:0;width:48px;
                  background:linear-gradient(270deg,#0F0F18,transparent);z-index:2;"></div>
      <p style="font-family:'Syne Mono',monospace;font-size:.6rem;
                color:rgba(167,139,250,.35);letter-spacing:.22em;white-space:nowrap;
                margin:0;padding:0 24px;">
        {effects}{effects}
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Hero + Stats ─────────────────────────────────────────────────────────
    hero_col, stat_col = st.columns([1.6, 1])

    with hero_col:
        st.markdown(f"""
        <div style="background:linear-gradient(145deg,#12111E,#1A1728);
                    border:1px solid rgba(167,139,250,.12);border-radius:20px;
                    padding:36px;height:100%;position:relative;overflow:hidden;
                    box-shadow:0 0 60px rgba(167,139,250,.06);">
          <div style="position:absolute;top:-80px;right:-80px;width:240px;height:240px;
                      background:radial-gradient(circle,rgba(167,139,250,.15) 0%,transparent 65%);
                      border-radius:50%;pointer-events:none;"></div>
          <div style="position:absolute;bottom:-50px;left:40px;width:160px;height:160px;
                      background:radial-gradient(circle,rgba(244,114,182,.08) 0%,transparent 65%);
                      border-radius:50%;pointer-events:none;"></div>
          <div style="display:inline-flex;align-items:center;gap:8px;
                      background:rgba(52,211,153,.06);border:1px solid rgba(52,211,153,.15);
                      border-radius:99px;padding:5px 14px;margin-bottom:20px;">
            <div style="width:6px;height:6px;border-radius:50%;background:#34D399;
                        box-shadow:0 0 8px rgba(52,211,153,.6);"></div>
            <span style="font-family:'Syne Mono',monospace;font-size:.58rem;color:#34D399;
                         text-transform:uppercase;letter-spacing:.1em;">Online</span>
          </div>
          <h1 style="font-family:'Syne',sans-serif;font-size:2.6rem;font-weight:800;
                     color:#EEEAF8;margin:0;letter-spacing:-.04em;line-height:1.05;position:relative;z-index:1;">
            Hey,
            <span style="background:linear-gradient(135deg,#A78BFA,#F472B6);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                         background-clip:text;">{uname}</span>
          </h1>
          <p style="font-family:'Outfit',sans-serif;font-size:.95rem;color:#7C7A9A;
                    margin:14px 0 0;position:relative;z-index:1;">
            {len(history)} artworks created &nbsp;&bull;&nbsp; {styles_used} styles explored
          </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Open Art Studio", type="primary", key="hero_create", use_container_width=True):
            st.session_state["page"] = "image_processing"
            st.rerun()

    with stat_col:
        STATS = [
            (len(history), "Artworks",    "#A78BFA", "rgba(167,139,250,.08)", "rgba(167,139,250,.15)"),
            (styles_used,  "Styles",      "#F472B6", "rgba(244,114,182,.08)", "rgba(244,114,182,.15)"),
            ("1.2s",       "Avg Speed",   "#60A5FA", "rgba(96,165,250,.08)",  "rgba(96,165,250,.15)"),
            (member_since[:7] if member_since != "-" else "-",
                           "Member",      "#34D399", "rgba(52,211,153,.08)",  "rgba(52,211,153,.15)"),
        ]
        r1, r2 = st.columns(2)
        for idx, (val, lbl, accent, bg, brd) in enumerate(STATS):
            col = r1 if idx % 2 == 0 else r2
            with col:
                st.markdown(f"""
                <div style="background:{bg};border:1px solid {brd};border-radius:14px;
                            padding:18px;margin-bottom:8px;">
                  <p style="font-family:'Syne',sans-serif;font-weight:800;
                             font-size:1.6rem;color:#EEEAF8;margin:0;line-height:1;">{val}</p>
                  <p style="font-family:'Syne Mono',monospace;font-size:.58rem;
                             color:{accent};text-transform:uppercase;letter-spacing:.1em;
                             margin:7px 0 0;">{lbl}</p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

    # ── Quick Actions ────────────────────────────────────────────────────────
    st.markdown(
        '<p style="font-family:Syne Mono,monospace;font-size:.6rem;color:#3E3C58;'
        'text-transform:uppercase;letter-spacing:.18em;margin:0 0 14px;">Quick Access</p>',
        unsafe_allow_html=True
    )

    actions = [
        ("Art Studio",  "Transform photos into stunning art with 10 AI effects",    "image_processing",
         "#A78BFA","rgba(167,139,250,.08)","rgba(167,139,250,.15)",
         '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" stroke="currentColor" stroke-width="1.5" fill="none"/>'),
        ("My Gallery",  "Browse and manage your collection of created artworks",     "history",
         "#60A5FA","rgba(96,165,250,.08)","rgba(96,165,250,.15)",
         '<rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M3 9h18M9 21V9" stroke="currentColor" stroke-width="1.5"/>'),
        ("Profile",     "View stats, account details and manage your settings",      "profile",
         "#34D399","rgba(52,211,153,.08)","rgba(52,211,153,.15)",
         '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="1.5" fill="none"/><circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="1.5" fill="none"/>'),
    ]
    cols = st.columns(3)
    for col, (title, desc, pg, accent, bg, brd, icon_path) in zip(cols, actions):
        with col:
            st.markdown(f"""
            <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.06);
                        border-radius:16px;padding:22px;margin-bottom:8px;
                        position:relative;overflow:hidden;
                        box-shadow:0 4px 20px rgba(0,0,0,.3);">
              <div style="position:absolute;top:0;right:0;width:80px;height:80px;
                          background:radial-gradient(circle,{bg} 0%,transparent 70%);"></div>
              <div style="width:38px;height:38px;border-radius:10px;background:{bg};
                          border:1px solid {brd};display:flex;align-items:center;
                          justify-content:center;margin-bottom:14px;">
                <svg width="18" height="18" viewBox="0 0 24 24" style="color:{accent}">
                  {icon_path}
                </svg>
              </div>
              <p style="font-family:'Syne',sans-serif;font-weight:700;
                        font-size:.95rem;color:#EEEAF8;margin:0 0 5px;">{title}</p>
              <p style="font-family:'Outfit',sans-serif;font-size:.8rem;
                        color:#7C7A9A;margin:0;line-height:1.5;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Go to {title}", key=f"dash_{pg}", use_container_width=True):
                st.session_state["page"] = pg
                st.rerun()

    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

    # ── Recent Artworks + Activity ───────────────────────────────────────────
    recent_col, log_col = st.columns([2.2, 1])

    GRAD = [
        "linear-gradient(135deg,#1A1728,#201630)",
        "linear-gradient(135deg,#0F1A28,#0F2018)",
        "linear-gradient(135deg,#200F18,#1A1014)",
        "linear-gradient(135deg,#1A1420,#0F1428)",
    ]

    with recent_col:
        st.markdown("""
        <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.06);
                    border-radius:16px;padding:20px;margin-bottom:0;
                    box-shadow:0 4px 20px rgba(0,0,0,.3);">
          <p style="font-family:'Syne',sans-serif;font-weight:700;
                    font-size:.95rem;color:#EEEAF8;margin:0 0 16px;">Recent Artworks</p>
        </div>
        """, unsafe_allow_html=True)

        if history:
            recent   = history[:4]
            img_cols = st.columns(min(len(recent), 4))
            for i, (ic, item) in enumerate(zip(img_cols, recent)):
                with ic:
                    ppath = item.get("processed_image_path", "")
                    if ppath and os.path.exists(ppath):
                        st.image(ppath, use_container_width=True)
                    else:
                        st.markdown(
                            f'<div style="aspect-ratio:1;border-radius:10px;'
                            f'background:{GRAD[i%4]};display:flex;align-items:center;'
                            f'justify-content:center;font-size:1.8rem;'
                            f'border:1px solid rgba(255,255,255,.06);">&#128444;</div>',
                            unsafe_allow_html=True
                        )
                    style = item.get("style_applied", "-")
                    date  = (item.get("processing_date") or "")[:10]
                    st.markdown(
                        f'<div style="padding:6px 0 0;">'
                        f'<p style="font-family:Outfit,sans-serif;font-weight:600;'
                        f'font-size:.78rem;color:#EEEAF8;margin:0;">{style}</p>'
                        f'<p style="font-family:Syne Mono,monospace;font-size:.58rem;'
                        f'color:#3E3C58;margin:2px 0 0;">{date}</p></div>',
                        unsafe_allow_html=True
                    )
        else:
            st.markdown("""
            <div style="padding:40px;text-align:center;">
              <p style="font-family:'Syne',sans-serif;font-size:.95rem;
                        font-weight:700;color:#3E3C58;margin:0 0 4px;">No artworks yet</p>
              <p style="font-family:'Outfit',sans-serif;font-size:.82rem;
                        color:#3E3C58;margin:0 0 16px;">Head to Art Studio to create</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Creating", type="primary", key="dash_empty_cta"):
                st.session_state["page"] = "image_processing"
                st.rerun()

    with log_col:
        DOTS  = ["#A78BFA","#F472B6","#60A5FA","#34D399"]
        ACTS  = [
            ("Applied","Classic Cartoon","portrait.jpg","2m ago"),
            ("Downloaded","Neon Glow","","1h ago"),
            ("Uploaded","cityscape.png","","3h ago"),
            ("Applied","Vintage","family.jpg","Yesterday"),
        ]
        if history:
            ACTS = [(
                "Applied", h.get("style_applied","-"),
                os.path.basename(h.get("original_image_path","")),
                (h.get("processing_date","") or "")[:10]
            ) for h in history[:4]]

        cards = "".join([
            f'<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:14px;">'
            f'<div style="width:7px;height:7px;border-radius:50%;background:{DOTS[i]};'
            f'margin-top:5px;flex-shrink:0;box-shadow:0 0 6px {DOTS[i]};"></div>'
            f'<div><p style="font-family:Outfit,sans-serif;font-size:.8rem;'
            f'color:#EEEAF8;margin:0;line-height:1.4;">{verb} <strong>{style}</strong>'
            f'{(" / "+fname) if fname else ""}</p>'
            f'<p style="font-family:Syne Mono,monospace;font-size:.58rem;color:#3E3C58;'
            f'margin:2px 0 0;">{when}</p></div></div>'
            for i,(verb,style,fname,when) in enumerate(ACTS)
        ])

        st.markdown(f"""
        <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.06);
                    border-radius:16px;padding:20px;height:100%;
                    box-shadow:0 4px 20px rgba(0,0,0,.3);">
          <p style="font-family:'Syne',sans-serif;font-weight:700;
                    font-size:.95rem;color:#EEEAF8;margin:0 0 16px;">Activity</p>
          {cards}
        </div>
        """, unsafe_allow_html=True)