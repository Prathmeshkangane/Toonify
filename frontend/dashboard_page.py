import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.auth import get_image_history
from database.db import get_connection


def _global_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Outfit:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

    html, body, .stApp { background:#06060E !important; }
    #MainMenu, footer, header[data-testid="stHeader"],
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] { display:none !important; }
    .block-container { padding: 24px 32px 48px !important; max-width: 1300px !important; }

    /* metric cards */
    [data-testid="stMetric"] {
        background: rgba(255,255,255,.025) !important;
        border: 1px solid rgba(255,255,255,.06) !important;
        border-radius: 14px !important;
        padding: 14px 16px !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Syne', sans-serif !important;
        color: #F0ECF8 !important;
        font-size: 1.4rem !important;
    }
    [data-testid="stMetricLabel"] {
        font-family: 'Space Mono', monospace !important;
        color: rgba(255,255,255,.3) !important;
        font-size: .6rem !important;
        text-transform: uppercase !important;
        letter-spacing: .1em !important;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg,#9370DB,#C471ED) !important;
        color: #fff !important; border: none !important;
        border-radius: 12px !important; height: 44px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important; font-size: .88rem !important;
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
        font-size: .85rem !important; transition: all .18s ease !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        border-color: rgba(147,112,219,.3) !important;
        color: #C471ED !important;
        background: rgba(147,112,219,.05) !important;
        transform: translateY(-1px) !important;
    }
    </style>
    """, unsafe_allow_html=True)


def show_dashboard():
    _global_styles()

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

    # ── Top nav bar ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                padding:0 0 28px;border-bottom:1px solid rgba(255,255,255,.05);
                margin-bottom:32px;">
      <div style="display:flex;align-items:center;gap:12px;">
        <div style="width:36px;height:36px;border-radius:10px;
                    background:linear-gradient(135deg,#9370DB,#C471ED);
                    display:flex;align-items:center;justify-content:center;
                    box-shadow:0 4px 16px rgba(147,112,219,.5);">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" fill="rgba(255,255,255,.15)"/>
            <path d="M8 12l3 3 5-5" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span style="font-family:'Syne',sans-serif;font-weight:800;font-size:1rem;
                     color:#F0ECF8;letter-spacing:-.03em;">CartoonizeMe</span>
      </div>
      <div style="display:flex;align-items:center;gap:10px;">
        <div style="display:flex;align-items:center;gap:7px;
                    background:rgba(52,211,153,.06);border:1px solid rgba(52,211,153,.14);
                    border-radius:99px;padding:5px 13px;">
          <div style="width:5px;height:5px;border-radius:50%;background:#34D399;
                      box-shadow:0 0 8px rgba(52,211,153,.9);"></div>
          <span style="font-family:'Space Mono',monospace;font-size:.58rem;color:#34D399;
                       text-transform:uppercase;letter-spacing:.1em;">Online</span>
        </div>
        <div style="width:34px;height:34px;border-radius:10px;
                    background:linear-gradient(135deg,#9370DB,#C471ED);
                    display:flex;align-items:center;justify-content:center;
                    font-family:'Syne',sans-serif;font-weight:800;font-size:.85rem;color:#fff;
                    box-shadow:0 2px 10px rgba(147,112,219,.4);">{uname[0].upper()}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Ticker ───────────────────────────────────────────────────────────────
    effects_text = ("CLASSIC CARTOON &nbsp;/&nbsp; WATERCOLOR &nbsp;/&nbsp; NEON GLOW &nbsp;/&nbsp; "
                    "ANIME &nbsp;/&nbsp; PENCIL SKETCH &nbsp;/&nbsp; OIL PAINT &nbsp;/&nbsp; "
                    "VINTAGE &nbsp;/&nbsp; PIXEL ART &nbsp;/&nbsp; COMIC BOOK &nbsp;/&nbsp; "
                    "COLOR PENCIL &nbsp;&nbsp;&nbsp;&nbsp;")
    st.markdown(f"""
    <div style="background:rgba(147,112,219,.04);border:1px solid rgba(147,112,219,.1);
                border-radius:12px;padding:10px 0;margin-bottom:32px;overflow:hidden;
                position:relative;">
      <div style="position:absolute;left:0;top:0;bottom:0;width:60px;
                  background:linear-gradient(90deg,#06060E,transparent);z-index:2;"></div>
      <div style="position:absolute;right:0;top:0;bottom:0;width:60px;
                  background:linear-gradient(270deg,#06060E,transparent);z-index:2;"></div>
      <p style="font-family:'Space Mono',monospace;font-size:.58rem;
                color:rgba(147,112,219,.35);letter-spacing:.2em;white-space:nowrap;
                margin:0;padding:0 24px;animation:ticker 30s linear infinite;">
        {effects_text * 2}
      </p>
    </div>
    <style>
    @keyframes ticker {{
      0% {{ transform: translateX(0); }}
      100% {{ transform: translateX(-50%); }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # ── Hero ─────────────────────────────────────────────────────────────────
    hero_col, stat_col = st.columns([1.6, 1])

    with hero_col:
        st.markdown(f"""
        <div style="background:linear-gradient(145deg,#0D0B18,#160D22,#1A0F2E);
                    border:1px solid rgba(147,112,219,.12);border-radius:22px;
                    padding:38px;position:relative;overflow:hidden;
                    box-shadow:0 0 80px rgba(147,112,219,.07);">
          <!-- BG Orbs -->
          <div style="position:absolute;top:-80px;right:-80px;width:260px;height:260px;
                      background:radial-gradient(circle,rgba(147,112,219,.18) 0%,transparent 65%);
                      border-radius:50%;pointer-events:none;"></div>
          <div style="position:absolute;bottom:-50px;left:40px;width:180px;height:180px;
                      background:radial-gradient(circle,rgba(246,79,89,.08) 0%,transparent 65%);
                      border-radius:50%;pointer-events:none;"></div>
          <!-- Corner grid pattern -->
          <div style="position:absolute;top:0;right:0;width:200px;height:200px;
                      background-image:linear-gradient(rgba(147,112,219,.04) 1px,transparent 1px),
                                       linear-gradient(90deg,rgba(147,112,219,.04) 1px,transparent 1px);
                      background-size:24px 24px;pointer-events:none;opacity:.6;"></div>

          <p style="font-family:'Space Mono',monospace;font-size:.6rem;
                    color:rgba(147,112,219,.5);letter-spacing:.14em;
                    text-transform:uppercase;margin:0 0 16px;position:relative;z-index:1;">
            Dashboard
          </p>
          <h1 style="font-family:'Syne',sans-serif;font-size:2.8rem;font-weight:800;
                     color:#F0ECF8;margin:0;letter-spacing:-.05em;line-height:1.05;
                     position:relative;z-index:1;">
            Hey,&nbsp;
            <span style="background:linear-gradient(135deg,#9370DB,#C471ED,#F64F59);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                         background-clip:text;">{uname}</span> 👋
          </h1>
          <p style="font-family:'Outfit',sans-serif;font-size:.92rem;color:rgba(255,255,255,.3);
                    margin:14px 0 0;position:relative;z-index:1;line-height:1.6;">
            {len(history)} artworks created &nbsp;&bull;&nbsp; {styles_used} styles explored &nbsp;&bull;&nbsp; Member since {member_since[:7] if member_since != "-" else "-"}
          </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("🎨 Open Art Studio", type="primary", key="hero_create", use_container_width=True):
            st.session_state["page"] = "image_processing"
            st.rerun()

    with stat_col:
        STATS = [
            (len(history), "Artworks",  "#9370DB", "rgba(147,112,219,.07)", "rgba(147,112,219,.15)"),
            (styles_used,  "Styles",    "#C471ED", "rgba(196,113,237,.07)", "rgba(196,113,237,.15)"),
            ("Fast",       "Avg Speed", "#60A5FA", "rgba(96,165,250,.07)",  "rgba(96,165,250,.15)"),
            (member_since[:7] if member_since != "-" else "-",
                           "Member",   "#34D399", "rgba(52,211,153,.07)",  "rgba(52,211,153,.15)"),
        ]
        r1, r2 = st.columns(2)
        for idx, (val, lbl, accent, bg, brd) in enumerate(STATS):
            col = r1 if idx % 2 == 0 else r2
            with col:
                st.markdown(f"""
                <div style="background:{bg};border:1px solid {brd};border-radius:16px;
                            padding:18px;margin-bottom:10px;
                            position:relative;overflow:hidden;">
                  <div style="position:absolute;top:-16px;right:-16px;width:64px;height:64px;
                              background:radial-gradient(circle,{brd} 0%,transparent 70%);
                              border-radius:50%;pointer-events:none;"></div>
                  <p style="font-family:'Syne',sans-serif;font-weight:800;
                             font-size:1.7rem;color:#F0ECF8;margin:0;line-height:1;">{val}</p>
                  <p style="font-family:'Space Mono',monospace;font-size:.55rem;
                             color:{accent};text-transform:uppercase;letter-spacing:.1em;
                             margin:8px 0 0;">{lbl}</p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)

    # ── Quick Actions ─────────────────────────────────────────────────────────
    st.markdown(
        '<p style="font-family:Space Mono,monospace;font-size:.6rem;color:rgba(255,255,255,.2);'
        'text-transform:uppercase;letter-spacing:.18em;margin:0 0 16px;">Quick Access</p>',
        unsafe_allow_html=True
    )

    actions = [
        ("Art Studio", "Transform photos into stunning AI art with 10 unique effects",
         "image_processing", "#9370DB", "rgba(147,112,219,.07)", "rgba(147,112,219,.14)", "🎨"),
        ("My Gallery", "Browse and re-download your collection of created artworks",
         "history", "#60A5FA", "rgba(96,165,250,.07)", "rgba(96,165,250,.14)", "🖼️"),
        ("Profile", "View stats, account details, billing and security settings",
         "profile", "#34D399", "rgba(52,211,153,.07)", "rgba(52,211,153,.14)", "👤"),
    ]
    cols = st.columns(3)
    for col, (title, desc, pg, accent, bg, brd, emoji) in zip(cols, actions):
        with col:
            st.markdown(f"""
            <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.06);
                        border-radius:18px;padding:24px;margin-bottom:10px;
                        position:relative;overflow:hidden;
                        box-shadow:0 8px 32px rgba(0,0,0,.4);
                        transition:border-color .2s;">
              <div style="position:absolute;top:0;right:0;width:100px;height:100px;
                          background:radial-gradient(circle,{bg} 0%,transparent 70%);
                          pointer-events:none;"></div>
              <div style="width:42px;height:42px;border-radius:12px;background:{bg};
                          border:1px solid {brd};display:flex;align-items:center;
                          justify-content:center;margin-bottom:16px;font-size:1.2rem;">{emoji}</div>
              <p style="font-family:'Syne',sans-serif;font-weight:700;
                        font-size:.95rem;color:#F0ECF8;margin:0 0 6px;">{title}</p>
              <p style="font-family:'Outfit',sans-serif;font-size:.78rem;
                        color:rgba(255,255,255,.3);margin:0;line-height:1.55;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open {title}", key=f"dash_{pg}", use_container_width=True):
                st.session_state["page"] = pg
                st.rerun()

    st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)

    # ── Recent Artworks + Activity ────────────────────────────────────────────
    recent_col, log_col = st.columns([2.2, 1])

    GRAD = [
        "linear-gradient(135deg,#1A1728,#201630)",
        "linear-gradient(135deg,#0F1A28,#0F2018)",
        "linear-gradient(135deg,#200F18,#1A1014)",
        "linear-gradient(135deg,#1A1420,#0F1428)",
    ]

    with recent_col:
        st.markdown("""
        <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.06);
                    border-radius:18px;padding:22px 22px 14px;
                    box-shadow:0 8px 32px rgba(0,0,0,.3);">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;">
            <p style="font-family:'Syne',sans-serif;font-weight:700;
                      font-size:.95rem;color:#F0ECF8;margin:0;">Recent Artworks</p>
            <span style="font-family:'Space Mono',monospace;font-size:.57rem;
                         color:rgba(255,255,255,.2);letter-spacing:.1em;text-transform:uppercase;">
              Latest 4
            </span>
          </div>
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
                            f'<div style="aspect-ratio:1;border-radius:12px;'
                            f'background:{GRAD[i%4]};display:flex;align-items:center;'
                            f'justify-content:center;font-size:1.8rem;'
                            f'border:1px solid rgba(255,255,255,.05);">🖼</div>',
                            unsafe_allow_html=True
                        )
                    style = item.get("style_applied", "-")
                    short_style = style.split(" ", 1)[-1] if " " in style else style
                    date  = (item.get("processing_date") or "")[:10]
                    st.markdown(
                        f'<div style="padding:7px 0 0;">'
                        f'<p style="font-family:Outfit,sans-serif;font-weight:600;'
                        f'font-size:.76rem;color:#F0ECF8;margin:0;">{short_style}</p>'
                        f'<p style="font-family:Space Mono,monospace;font-size:.56rem;'
                        f'color:rgba(255,255,255,.2);margin:2px 0 0;">{date}</p></div>',
                        unsafe_allow_html=True
                    )
        else:
            st.markdown("""
            <div style="padding:50px;text-align:center;">
              <div style="font-size:2.5rem;margin-bottom:14px;opacity:.3;">🎨</div>
              <p style="font-family:'Syne',sans-serif;font-size:.92rem;
                        font-weight:700;color:rgba(255,255,255,.25);margin:0 0 6px;">No artworks yet</p>
              <p style="font-family:'Outfit',sans-serif;font-size:.8rem;
                        color:rgba(255,255,255,.18);margin:0 0 20px;">Head to Art Studio to create your first</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Creating ✨", type="primary", key="dash_empty_cta"):
                st.session_state["page"] = "image_processing"
                st.rerun()

    with log_col:
        DOTS  = ["#9370DB","#C471ED","#60A5FA","#34D399"]
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
            f'<div style="display:flex;align-items:flex-start;gap:11px;margin-bottom:16px;">'
            f'<div style="width:7px;height:7px;border-radius:50%;background:{DOTS[i]};'
            f'margin-top:6px;flex-shrink:0;box-shadow:0 0 8px {DOTS[i]};"></div>'
            f'<div><p style="font-family:Outfit,sans-serif;font-size:.79rem;'
            f'color:#F0ECF8;margin:0;line-height:1.4;">{verb} <strong style="color:#C471ED;">{style}</strong>'
            f'{(" · "+fname[:12]) if fname else ""}</p>'
            f'<p style="font-family:Space Mono,monospace;font-size:.56rem;color:rgba(255,255,255,.2);'
            f'margin:3px 0 0;">{when}</p></div></div>'
            for i,(verb,style,fname,when) in enumerate(ACTS)
        ])

        st.markdown(f"""
        <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.06);
                    border-radius:18px;padding:22px;height:100%;
                    box-shadow:0 8px 32px rgba(0,0,0,.3);">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;">
            <p style="font-family:'Syne',sans-serif;font-weight:700;
                      font-size:.95rem;color:#F0ECF8;margin:0;">Activity</p>
            <div style="width:6px;height:6px;border-radius:50%;background:#34D399;
                        box-shadow:0 0 8px rgba(52,211,153,.9);"></div>
          </div>
          {cards}
        </div>
        """, unsafe_allow_html=True)

    # ── Logout ────────────────────────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    _, logout_col, _ = st.columns([4, 1, 4])
    with logout_col:
        if st.button("Sign Out", key="logout_btn", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()