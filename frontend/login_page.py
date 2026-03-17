import streamlit as st
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit.components.v1 as components

# ── optional: comment out if you don't have this module yet ──
try:
    from backend.auth import login_user
except ImportError:
    def login_user(identifier, password):
        # stub – replace with real auth
        if identifier and password:
            return {"success": True, "user": {"username": identifier}}
        return {"success": False, "message": "Invalid credentials"}


def show_login_page():

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap');

    html, body, .stApp { margin:0 !important; padding:0 !important; background:#08080F !important; overflow-x:hidden !important; }
    #MainMenu, footer, header[data-testid="stHeader"],
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"]                     { display:none !important; }
    .block-container                                   { padding:0 !important; max-width:100% !important; }
    section[data-testid="stMain"] > div                { padding:0 !important; }
    [data-testid="column"]                             { padding:0 !important; gap:0 !important; }
    .stHorizontalBlock                                 { gap:0 !important; }

    .stTextInput > div > div > input {
        background: rgba(255,255,255,.04) !important;
        border: 1px solid rgba(255,255,255,.1) !important;
        border-radius: 10px !important;
        color: #EEEAF8 !important;
        padding: 13px 16px !important;
        font-size: .925rem !important;
        font-family: 'DM Sans', sans-serif !important;
        height: 46px !important;
        transition: border-color .18s, box-shadow .18s !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #A78BFA !important;
        box-shadow: 0 0 0 3px rgba(167,139,250,.15) !important;
        background: rgba(167,139,250,.04) !important;
        outline: none !important;
    }
    .stTextInput > div > div > input::placeholder { color: rgba(255,255,255,.2) !important; }
    .stTextInput label {
        font-family: 'DM Sans', sans-serif !important;
        font-size: .72rem !important;
        font-weight: 600 !important;
        color: rgba(255,255,255,.35) !important;
        text-transform: uppercase !important;
        letter-spacing: .1em !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #A78BFA 0%, #F472B6 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        height: 46px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: .95rem !important;
        letter-spacing: .01em !important;
        box-shadow: 0 4px 24px rgba(167,139,250,.35) !important;
        transition: all .2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 40px rgba(167,139,250,.5) !important;
    }

    .stButton > button:not([kind="primary"]) {
        background: rgba(255,255,255,.04) !important;
        color: rgba(255,255,255,.7) !important;
        border: 1px solid rgba(255,255,255,.1) !important;
        border-radius: 10px !important;
        height: 46px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: .9rem !important;
        transition: all .18s ease !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        border-color: rgba(167,139,250,.4) !important;
        color: #A78BFA !important;
        background: rgba(167,139,250,.06) !important;
        transform: translateY(-1px) !important;
    }

    .stCheckbox label span {
        color: rgba(255,255,255,.45) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: .85rem !important;
    }

    .stSuccess { background: rgba(52,211,153,.07) !important; border:1px solid rgba(52,211,153,.25) !important; border-radius:10px !important; }
    .stError   { background: rgba(244,114,182,.07) !important; border:1px solid rgba(244,114,182,.22) !important; border-radius:10px !important; }
    [data-testid="stAlert"] { font-family:'DM Sans',sans-serif !important; font-size:.875rem !important; border-left-width:0 !important; color:#EEEAF8 !important; }
    .stSpinner > div { border-top-color: #A78BFA !important; }

    /* Remove iframe border/bg */
    iframe { border: none !important; display: block !important; }
    </style>
    """, unsafe_allow_html=True)

    left, right = st.columns([9, 11])

    # ════════════ LEFT ════════════
    with left:
        st.markdown("""
        <div style="background:#08080F;padding:40px 56px 28px 56px;
                    border-right:1px solid rgba(255,255,255,.05);box-sizing:border-box;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:52px;">
            <div style="display:flex;align-items:center;gap:10px;">
              <div style="width:32px;height:32px;border-radius:9px;
                          background:linear-gradient(135deg,#A78BFA,#F472B6);
                          display:flex;align-items:center;justify-content:center;
                          box-shadow:0 4px 14px rgba(167,139,250,.4);">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                        stroke="white" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <span style="font-family:'Syne',sans-serif;font-weight:800;font-size:.95rem;
                           color:#EEEAF8;letter-spacing:-.025em;">CartoonizeMe</span>
            </div>
            <span style="font-family:'DM Sans',sans-serif;font-size:.83rem;color:rgba(255,255,255,.3);">
              New here?&nbsp;<span style="color:#A78BFA;font-weight:500;cursor:pointer;">Create account</span>
            </span>
          </div>

          <div style="margin-bottom:28px;">
            <div style="display:inline-flex;align-items:center;gap:8px;
                        background:rgba(167,139,250,.08);border:1px solid rgba(167,139,250,.18);
                        border-radius:99px;padding:5px 14px;margin-bottom:18px;">
              <div style="width:6px;height:6px;border-radius:50%;background:#A78BFA;
                          box-shadow:0 0 8px rgba(167,139,250,.8);"></div>
              <span style="font-family:'DM Sans',sans-serif;font-size:.72rem;font-weight:600;
                           color:#A78BFA;letter-spacing:.08em;text-transform:uppercase;">AI Art Studio</span>
            </div>
            <h1 style="font-family:'Syne',sans-serif;font-weight:800;font-size:2.2rem;
                       color:#EEEAF8;margin:0 0 10px;letter-spacing:-.04em;line-height:1.15;">
              Welcome back
            </h1>
            <p style="font-family:'DM Sans',sans-serif;font-size:.9rem;
                      color:rgba(255,255,255,.35);margin:0;line-height:1.6;">
              Sign in to continue creating stunning art
            </p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        _, fc, _ = st.columns([56, 999, 56])
        with fc:
            identifier = st.text_input(
                "Email or Username",
                placeholder="you@example.com",
                key="li_id",
            )
            show_pw = st.checkbox("Show password", key="li_show")
            password = st.text_input(
                "Password",
                type="default" if show_pw else "password",
                placeholder="Your password",
                key="li_pw",
            )

            st.markdown("""
            <div style="display:flex;justify-content:flex-end;margin:-4px 0 18px;">
              <span style="font-family:'DM Sans',sans-serif;font-size:.82rem;font-weight:500;
                           color:#A78BFA;cursor:pointer;">Forgot password?</span>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Sign in", use_container_width=True, type="primary", key="li_submit"):
                if not identifier or not password:
                    st.error("Please fill in all fields.")
                else:
                    with st.spinner(""):
                        result = login_user(identifier, password)
                    if result["success"]:
                        st.session_state.update({
                            "logged_in": True,
                            "user":      result["user"],
                            "page":      "dashboard",
                        })
                        st.rerun()
                    else:
                        st.error(result["message"])

            st.markdown("""
            <div style="display:flex;align-items:center;gap:12px;margin:18px 0 14px;">
              <div style="flex:1;height:1px;background:rgba(255,255,255,.07);"></div>
              <span style="font-family:'DM Sans',sans-serif;font-size:.72rem;
                           color:rgba(255,255,255,.22);letter-spacing:.08em;
                           text-transform:uppercase;white-space:nowrap;">New to CartoonizeMe?</span>
              <div style="flex:1;height:1px;background:rgba(255,255,255,.07);"></div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Create a free account", use_container_width=True, key="go_reg"):
                st.session_state["page"] = "register"
                st.rerun()

        st.markdown("""
        <div style="padding:20px 56px 32px;background:#08080F;
                    border-right:1px solid rgba(255,255,255,.05);">
          <p style="font-family:'DM Sans',sans-serif;font-size:.75rem;
                    color:rgba(255,255,255,.18);line-height:1.7;margin:0;">
            By signing in you agree to our
            <span style="color:rgba(255,255,255,.38);text-decoration:underline;cursor:pointer;">Terms of Service</span>
            and
            <span style="color:rgba(255,255,255,.38);text-decoration:underline;cursor:pointer;">Privacy Policy</span>.
          </p>
        </div>
        """, unsafe_allow_html=True)

    # ════════════ RIGHT — rendered via iframe to support full CSS ════════════
    with right:
        components.html("""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap" rel="stylesheet">
        <style>
          *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
          body {
            background: linear-gradient(145deg, #0D0B18 0%, #130920 50%, #1C0B28 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 60px 52px;
            position: relative;
            overflow: hidden;
            font-family: 'DM Sans', sans-serif;
          }

          /* ── glowing orbs ── */
          .orb { position: absolute; border-radius: 50%; pointer-events: none; }
          .orb-1 { top: -100px; right: -60px; width: 480px; height: 480px;
                   background: radial-gradient(circle, rgba(167,139,250,.18) 0%, transparent 60%); }
          .orb-2 { bottom: -80px; left: -80px; width: 420px; height: 420px;
                   background: radial-gradient(circle, rgba(244,114,182,.14) 0%, transparent 60%); }
          .orb-3 { top: 50%; left: 20%; width: 280px; height: 280px;
                   background: radial-gradient(circle, rgba(96,165,250,.08) 0%, transparent 65%); }

          /* ── dot grid ── */
          .grid {
            position: absolute; inset: 0; pointer-events: none;
            background-image: radial-gradient(rgba(255,255,255,.07) 1px, transparent 1px);
            background-size: 28px 28px;
          }

          /* ── top rainbow line ── */
          .top-line {
            position: absolute; top: 0; left: 0; right: 0; height: 1px;
            background: linear-gradient(90deg, transparent, #A78BFA 40%, #F472B6 60%, transparent);
            opacity: .6;
          }

          /* ── main content ── */
          .content {
            position: relative; z-index: 2;
            text-align: center; max-width: 400px; width: 100%;
          }

          /* icon */
          .icon-wrap {
            display: inline-flex; align-items: center; justify-content: center;
            width: 60px; height: 60px; border-radius: 18px; margin-bottom: 24px;
            background: linear-gradient(135deg, #A78BFA, #F472B6);
            box-shadow: 0 0 0 8px rgba(167,139,250,.08), 0 8px 32px rgba(167,139,250,.4);
          }

          /* headline */
          h2 {
            font-family: 'Syne', sans-serif; font-weight: 800; font-size: 2rem;
            color: #EEEAF8; margin: 0 0 12px; letter-spacing: -.04em; line-height: 1.15;
          }
          .gradient-text {
            background: linear-gradient(135deg, #A78BFA 0%, #F472B6 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
          }
          .subtitle {
            font-size: .88rem; color: rgba(255,255,255,.35);
            margin: 0 0 40px; line-height: 1.65;
          }

          /* ── feature cards ── */
          .cards {
            display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 36px;
          }
          .card {
            background: rgba(255,255,255,.03);
            border: 1px solid rgba(255,255,255,.07);
            border-radius: 14px; padding: 18px 16px; text-align: left;
            backdrop-filter: blur(12px);
            transition: border-color .2s, background .2s, transform .2s;
          }
          .card:hover {
            border-color: rgba(167,139,250,.25);
            background: rgba(167,139,250,.04);
            transform: translateY(-2px);
          }
          .card-emoji { font-size: 1.4rem; margin-bottom: 10px; }
          .card-title {
            font-family: 'Syne', sans-serif; font-weight: 700; font-size: .85rem;
            color: #EEEAF8; margin: 0 0 4px;
          }
          .card-desc {
            font-size: .75rem; color: rgba(255,255,255,.28); margin: 0; line-height: 1.5;
          }

          /* ── badges ── */
          .badges { display: flex; align-items: center; justify-content: center; gap: 6px; flex-wrap: wrap; }
          .badge {
            display: flex; align-items: center; gap: 6px;
            border-radius: 99px; padding: 5px 12px;
            font-size: .75rem; color: rgba(255,255,255,.4); font-weight: 500;
          }
          .badge-green  { background: rgba(52,211,153,.06);  border: 1px solid rgba(52,211,153,.15); }
          .badge-purple { background: rgba(167,139,250,.06); border: 1px solid rgba(167,139,250,.15); }
          .badge-pink   { background: rgba(244,114,182,.06); border: 1px solid rgba(244,114,182,.15); }
          .dot { width: 5px; height: 5px; border-radius: 50%; }
          .dot-green  { background: #34D399; box-shadow: 0 0 6px rgba(52,211,153,.8); }
          .dot-purple { background: #A78BFA; box-shadow: 0 0 6px rgba(167,139,250,.8); }
          .dot-pink   { background: #F472B6; box-shadow: 0 0 6px rgba(244,114,182,.8); }

          /* ── footer ── */
          .footer {
            position: absolute; bottom: 24px; text-align: center; z-index: 2; width: 100%;
            font-size: .68rem; color: rgba(255,255,255,.12);
            letter-spacing: .18em; text-transform: uppercase;
            font-family: 'DM Sans', sans-serif;
          }

          /* ── entrance animations ── */
          @keyframes fadeUp {
            from { opacity: 0; transform: translateY(20px); }
            to   { opacity: 1; transform: translateY(0); }
          }
          .content       { animation: fadeUp .6s ease both; }
          .card:nth-child(1) { animation: fadeUp .5s .1s ease both; }
          .card:nth-child(2) { animation: fadeUp .5s .2s ease both; }
          .card:nth-child(3) { animation: fadeUp .5s .3s ease both; }
          .card:nth-child(4) { animation: fadeUp .5s .4s ease both; }
        </style>
        </head>
        <body>

          <!-- background layers -->
          <div class="orb orb-1"></div>
          <div class="orb orb-2"></div>
          <div class="orb orb-3"></div>
          <div class="grid"></div>
          <div class="top-line"></div>

          <!-- main content -->
          <div class="content">

            <div class="icon-wrap">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                      stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>

            <h2>
              Turn photos into<br>
              <span class="gradient-text">stunning art</span>
            </h2>
            <p class="subtitle">10 AI-powered effects. No watermarks.<br>Free forever.</p>

            <div class="cards">
              <div class="card">
                <div class="card-emoji">🎨</div>
                <p class="card-title">Classic Cartoon</p>
                <p class="card-desc">Bold outlines &amp; vibrant flat colors</p>
              </div>
              <div class="card">
                <div class="card-emoji">✏️</div>
                <p class="card-title">Pencil Sketch</p>
                <p class="card-desc">Realistic grayscale pencil effect</p>
              </div>
              <div class="card">
                <div class="card-emoji">🌊</div>
                <p class="card-title">Watercolor</p>
                <p class="card-desc">Soft flowing watercolor painting</p>
              </div>
              <div class="card">
                <div class="card-emoji">⚡</div>
                <p class="card-title">Neon Glow</p>
                <p class="card-desc">Cyberpunk neon edge effect</p>
              </div>
            </div>

            <div class="badges">
              <div class="badge badge-green">
                <div class="dot dot-green"></div>
                Free forever
              </div>
              <div class="badge badge-purple">
                <div class="dot dot-purple"></div>
                No watermarks
              </div>
              <div class="badge badge-pink">
                <div class="dot dot-pink"></div>
                10 AI effects
              </div>
            </div>

          </div>

          <div class="footer">CartoonizeMe · AI Art Studio · v2.0</div>

        </body>
        </html>
        """, height=900, scrolling=False)


# ── entrypoint ──────────────────────────────────────────────
if __name__ == "__main__":
    st.set_page_config(
        page_title="CartoonizeMe – Sign In",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    if st.session_state["page"] == "login":
        show_login_page()
    elif st.session_state["page"] == "dashboard":
        st.write(f"Welcome, {st.session_state['user']['username']}!")