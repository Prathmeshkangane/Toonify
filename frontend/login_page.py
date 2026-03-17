import streamlit as st
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import streamlit.components.v1 as components

try:
    from backend.auth import login_user
except ImportError:
    def login_user(identifier, password):
        if identifier and password:
            return {"success": True, "user": {"username": identifier}}
        return {"success": False, "message": "Invalid credentials"}


def show_login_page():

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&family=Clash+Display:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Outfit:wght@300;400;500;600;700&display=swap');

    html, body, .stApp { margin:0 !important; padding:0 !important; background:#06060E !important; overflow-x:hidden !important; }
    #MainMenu, footer, header[data-testid="stHeader"],
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] { display:none !important; }
    .block-container { padding:0 !important; max-width:100% !important; }
    section[data-testid="stMain"] > div { padding:0 !important; }
    [data-testid="column"] { padding:0 !important; gap:0 !important; }
    .stHorizontalBlock { gap:0 !important; }

    /* ── Input Fields ── */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,.035) !important;
        border: 1px solid rgba(255,255,255,.08) !important;
        border-radius: 14px !important;
        color: #F0ECF8 !important;
        padding: 14px 18px !important;
        font-size: .92rem !important;
        font-family: 'Outfit', sans-serif !important;
        height: 50px !important;
        transition: all .2s ease !important;
        letter-spacing: .01em !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(147,112,219,.6) !important;
        box-shadow: 0 0 0 4px rgba(147,112,219,.08), 0 0 20px rgba(147,112,219,.12) !important;
        background: rgba(147,112,219,.04) !important;
        outline: none !important;
    }
    .stTextInput > div > div > input::placeholder { color: rgba(255,255,255,.18) !important; }
    .stTextInput label {
        font-family: 'Space Mono', monospace !important;
        font-size: .65rem !important;
        font-weight: 400 !important;
        color: rgba(255,255,255,.3) !important;
        text-transform: uppercase !important;
        letter-spacing: .14em !important;
        margin-bottom: 6px !important;
    }

    /* ── Primary Button ── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #9370DB 0%, #C471ED 50%, #F64F59 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 14px !important;
        height: 50px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: .92rem !important;
        letter-spacing: .03em !important;
        box-shadow: 0 4px 30px rgba(147,112,219,.3), 0 0 0 1px rgba(147,112,219,.1) !important;
        transition: all .25s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 40px rgba(147,112,219,.45), 0 0 0 1px rgba(147,112,219,.2) !important;
    }
    .stButton > button[kind="primary"]:active { transform: translateY(0) !important; }

    /* ── Secondary Button ── */
    .stButton > button:not([kind="primary"]) {
        background: rgba(255,255,255,.03) !important;
        color: rgba(255,255,255,.6) !important;
        border: 1px solid rgba(255,255,255,.08) !important;
        border-radius: 14px !important;
        height: 50px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important;
        font-size: .88rem !important;
        transition: all .2s ease !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        border-color: rgba(147,112,219,.35) !important;
        color: #C471ED !important;
        background: rgba(147,112,219,.05) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Checkbox ── */
    .stCheckbox label span {
        color: rgba(255,255,255,.4) !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: .83rem !important;
    }

    /* ── Alerts ── */
    .stSuccess { background: rgba(52,211,153,.06) !important; border:1px solid rgba(52,211,153,.2) !important; border-radius:12px !important; }
    .stError   { background: rgba(246,79,89,.06) !important; border:1px solid rgba(246,79,89,.18) !important; border-radius:12px !important; }
    [data-testid="stAlert"] { font-family:'Outfit',sans-serif !important; font-size:.875rem !important; border-left-width:0 !important; color:#F0ECF8 !important; }
    .stSpinner > div { border-top-color: #9370DB !important; }

    iframe { border: none !important; display: block !important; }
    </style>
    """, unsafe_allow_html=True)

    left, right = st.columns([9, 11])

    # ════════════ LEFT ════════════
    with left:
        # Logo bar
        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:40px 60px 0;margin-bottom:48px;">
          <div style="display:flex;align-items:center;gap:11px;">
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
                         color:#F0ECF8;letter-spacing:-.03em;">Toonify</span>
          </div>
          <div style="font-family:'Outfit',sans-serif;font-size:.82rem;color:rgba(255,255,255,.25);">
            New here?&nbsp;<span style="color:#C471ED;font-weight:600;cursor:pointer;">Create account &#x2197;</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Heading
        st.markdown("""
        <div style="padding:0 60px;margin-bottom:28px;">
          <div style="display:inline-flex;align-items:center;gap:7px;
                      background:rgba(147,112,219,.07);border:1px solid rgba(147,112,219,.15);
                      border-radius:99px;padding:4px 13px;margin-bottom:18px;">
            <div style="width:5px;height:5px;border-radius:50%;background:#C471ED;
                        box-shadow:0 0 8px rgba(196,113,237,.9);"></div>
            <span style="font-family:'Space Mono',monospace;font-size:.6rem;
                         color:#C471ED;letter-spacing:.12em;text-transform:uppercase;">AI Art Studio</span>
          </div>
          <h1 style="font-family:'Syne',sans-serif;font-weight:800;font-size:2.6rem;
                     color:#F0ECF8;margin:0 0 12px;letter-spacing:-.05em;line-height:1.1;">
            Welcome<br>
            <span style="background:linear-gradient(135deg,#9370DB,#C471ED,#F64F59);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                         background-clip:text;">back.</span>
          </h1>
          <p style="font-family:'Outfit',sans-serif;font-size:.9rem;
                    color:rgba(255,255,255,.3);margin:0;line-height:1.65;">
            Sign in to continue creating stunning AI artworks
          </p>
        </div>
        """, unsafe_allow_html=True)

        _, fc, _ = st.columns([60, 999, 60])
        with fc:
            identifier = st.text_input(
                "Email or Username",
                placeholder="you@example.com",
                key="li_id",
            )
            
            if "li_show" not in st.session_state:
                st.session_state.li_show = False

            # 2. Use the session state value for the toggle logic
            password = st.text_input(
                "Password",
                type="default" if st.session_state.li_show else "password",
                placeholder="Your password",
                key="li_pw",
            )

            # 3. Now place the checkbox below the input
            st.checkbox("Show password", key="li_show")
            st.markdown("""
            <div style="display:flex;justify-content:flex-end;margin:-2px 0 20px;">
              <span style="font-family:'Outfit',sans-serif;font-size:.82rem;font-weight:500;
                           color:#9370DB;cursor:pointer;opacity:.8;">Forgot password?</span>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Sign in →", use_container_width=True, type="primary", key="li_submit"):
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
            <div style="display:flex;align-items:center;gap:14px;margin:22px 0 18px;">
              <div style="flex:1;height:1px;background:rgba(255,255,255,.06);"></div>
              <span style="font-family:'Space Mono',monospace;font-size:.6rem;
                           color:rgba(255,255,255,.18);letter-spacing:.12em;
                           text-transform:uppercase;white-space:nowrap;">New to Toofiny?</span>
              <div style="flex:1;height:1px;background:rgba(255,255,255,.06);"></div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Create a free account", use_container_width=True, key="go_reg"):
                st.session_state["page"] = "register"
                st.rerun()

        st.markdown("""
        <div style="padding:20px 60px 32px;background:#06060E;
                    border-right:1px solid rgba(255,255,255,.04);">
          <p style="font-family:'Outfit',sans-serif;font-size:.73rem;
                    color:rgba(255,255,255,.15);line-height:1.7;margin:0;">
            By signing in you agree to our
            <span style="color:rgba(255,255,255,.3);text-decoration:underline;cursor:pointer;">Terms of Service</span>
            and
            <span style="color:rgba(255,255,255,.3);text-decoration:underline;cursor:pointer;">Privacy Policy</span>.
          </p>
        </div>
        """, unsafe_allow_html=True)

    # ════════════ RIGHT ════════════
    with right:
        components.html("""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Outfit:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
        <style>
          *, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }
          body {
            background: #06060E;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 60px 50px;
            position: relative;
            overflow: hidden;
            font-family: 'Outfit', sans-serif;
          }

          /* Background layers */
          .noise {
            position: absolute; inset: 0; pointer-events: none; opacity: .025;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
            background-size: 200px 200px;
          }
          .grid {
            position: absolute; inset: 0; pointer-events: none;
            background-image: linear-gradient(rgba(147,112,219,.04) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(147,112,219,.04) 1px, transparent 1px);
            background-size: 40px 40px;
          }
          .orb {
            position: absolute; border-radius: 50%; pointer-events: none; filter: blur(1px);
          }
          .orb-1 {
            top: -120px; right: -80px; width: 500px; height: 500px;
            background: radial-gradient(circle, rgba(147,112,219,.14) 0%, transparent 65%);
          }
          .orb-2 {
            bottom: -100px; left: -60px; width: 440px; height: 440px;
            background: radial-gradient(circle, rgba(246,79,89,.1) 0%, transparent 65%);
          }
          .orb-3 {
            top: 45%; left: 15%; width: 320px; height: 320px;
            background: radial-gradient(circle, rgba(196,113,237,.06) 0%, transparent 65%);
          }

          /* Content */
          .content {
            position: relative; z-index: 2;
            text-align: center; max-width: 420px; width: 100%;
          }

          /* Floating image preview mockup */
          .mockup-container {
            position: relative;
            margin-bottom: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
          }

          .mockup-card {
            background: rgba(255,255,255,.03);
            border: 1px solid rgba(255,255,255,.07);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 24px 60px rgba(0,0,0,.5);
            animation: floatCard 6s ease-in-out infinite;
            flex-shrink: 0;
          }
          .mockup-card.main {
            width: 160px;
            animation-delay: 0s;
          }
          .mockup-card.side {
            width: 110px;
            opacity: .65;
          }
          .mockup-card.side.left {
            animation: floatCardL 6s ease-in-out infinite;
            animation-delay: 1s;
            transform: rotate(-8deg);
          }
          .mockup-card.side.right {
            animation: floatCardR 6s ease-in-out infinite;
            animation-delay: 2s;
            transform: rotate(8deg);
          }

          .img-placeholder {
            aspect-ratio: 0.85;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            position: relative;
            overflow: hidden;
          }
          .img-placeholder.p1 {
            background: linear-gradient(145deg,#1a0f2e,#2d1a4d,#1a1232);
          }
          .img-placeholder.p2 {
            background: linear-gradient(145deg,#0d1a2e,#1a2d4d,#0d1832);
          }
          .img-placeholder.p3 {
            background: linear-gradient(145deg,#2e0f1a,#4d1a2d,#320d18);
          }

          .effect-label {
            padding: 8px 12px;
            background: rgba(0,0,0,.4);
            border-top: 1px solid rgba(255,255,255,.06);
          }
          .effect-label p {
            font-family: 'Space Mono', monospace;
            font-size: .58rem;
            color: rgba(255,255,255,.5);
            text-transform: uppercase;
            letter-spacing: .1em;
            margin: 0;
          }

          /* Floating badge */
          .float-badge {
            position: absolute;
            top: -8px; right: -16px;
            background: linear-gradient(135deg,#9370DB,#C471ED);
            border-radius: 99px;
            padding: 4px 10px;
            font-family: 'Space Mono', monospace;
            font-size: .55rem;
            color: white;
            letter-spacing: .06em;
            text-transform: uppercase;
            box-shadow: 0 4px 14px rgba(147,112,219,.5);
            animation: pulse 2s ease-in-out infinite;
            white-space: nowrap;
          }

          h2 {
            font-family: 'Syne', sans-serif;
            font-weight: 800;
            font-size: 1.8rem;
            color: #F0ECF8;
            margin: 0 0 12px;
            letter-spacing: -.04em;
            line-height: 1.15;
          }
          .gradient-text {
            background: linear-gradient(135deg, #9370DB, #C471ED, #F64F59);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
          }
          .subtitle {
            font-size: .87rem;
            color: rgba(255,255,255,.3);
            margin: 0 0 36px;
            line-height: 1.7;
          }

          /* Effect cards grid */
          .effects-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 8px;
            margin-bottom: 32px;
          }
          .effect-chip {
            background: rgba(255,255,255,.03);
            border: 1px solid rgba(255,255,255,.07);
            border-radius: 12px;
            padding: 10px 4px;
            text-align: center;
            cursor: default;
            transition: all .3s ease;
          }
          .effect-chip:hover {
            background: rgba(147,112,219,.08);
            border-color: rgba(147,112,219,.25);
            transform: translateY(-3px);
          }
          .effect-chip .emoji { font-size: 1.2rem; display: block; margin-bottom: 4px; }
          .effect-chip .name {
            font-family: 'Space Mono', monospace;
            font-size: .5rem;
            color: rgba(255,255,255,.3);
            text-transform: uppercase;
            letter-spacing: .06em;
          }

          /* Stat pills */
          .stat-row {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            flex-wrap: wrap;
          }
          .stat-pill {
            display: flex;
            align-items: center;
            gap: 6px;
            border-radius: 99px;
            padding: 5px 12px;
            font-size: .73rem;
            color: rgba(255,255,255,.4);
            font-weight: 500;
          }
          .pill-green  { background: rgba(52,211,153,.05);  border: 1px solid rgba(52,211,153,.14); }
          .pill-purple { background: rgba(147,112,219,.05); border: 1px solid rgba(147,112,219,.14); }
          .pill-red    { background: rgba(246,79,89,.05);   border: 1px solid rgba(246,79,89,.14); }
          .dot { width: 5px; height: 5px; border-radius: 50%; }
          .dot-green  { background: #34D399; box-shadow: 0 0 7px rgba(52,211,153,.9); }
          .dot-purple { background: #9370DB; box-shadow: 0 0 7px rgba(147,112,219,.9); }
          .dot-red    { background: #F64F59; box-shadow: 0 0 7px rgba(246,79,89,.9); }

          /* Animations */
          @keyframes floatCard {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-12px); }
          }
          @keyframes floatCardL {
            0%, 100% { transform: translateY(0px) rotate(-8deg); }
            50% { transform: translateY(-8px) rotate(-8deg); }
          }
          @keyframes floatCardR {
            0%, 100% { transform: translateY(0px) rotate(8deg); }
            50% { transform: translateY(-10px) rotate(8deg); }
          }
          @keyframes pulse {
            0%, 100% { box-shadow: 0 4px 14px rgba(147,112,219,.5); }
            50% { box-shadow: 0 4px 24px rgba(147,112,219,.8); }
          }
          @keyframes fadeUp {
            from { opacity: 0; transform: translateY(24px); }
            to   { opacity: 1; transform: translateY(0); }
          }
          .content { animation: fadeUp .7s ease both; }
          .effect-chip:nth-child(1) { animation: fadeUp .4s .05s ease both; }
          .effect-chip:nth-child(2) { animation: fadeUp .4s .1s ease both; }
          .effect-chip:nth-child(3) { animation: fadeUp .4s .15s ease both; }
          .effect-chip:nth-child(4) { animation: fadeUp .4s .2s ease both; }
          .effect-chip:nth-child(5) { animation: fadeUp .4s .25s ease both; }
          .effect-chip:nth-child(6) { animation: fadeUp .4s .3s ease both; }
          .effect-chip:nth-child(7) { animation: fadeUp .4s .35s ease both; }
          .effect-chip:nth-child(8) { animation: fadeUp .4s .4s ease both; }
          .effect-chip:nth-child(9) { animation: fadeUp .4s .45s ease both; }
          .effect-chip:nth-child(10){ animation: fadeUp .4s .5s ease both; }

          .footer {
            position: absolute; bottom: 20px; text-align: center;
            z-index: 2; width: 100%;
            font-family: 'Space Mono', monospace;
            font-size: .58rem; color: rgba(255,255,255,.1);
            letter-spacing: .14em; text-transform: uppercase;
          }
        </style>
        </head>
        <body>
          <div class="noise"></div>
          <div class="grid"></div>
          <div class="orb orb-1"></div>
          <div class="orb orb-2"></div>
          <div class="orb orb-3"></div>

          <div class="content">
            <!-- Floating cards mockup -->
            <div class="mockup-container">
              <div class="mockup-card side left">
                <div class="img-placeholder p2">🌊</div>
                <div class="effect-label"><p>Watercolor</p></div>
              </div>

              <div class="mockup-card main" style="position:relative;">
                <div class="float-badge">✨ AI Magic</div>
                <div class="img-placeholder p1" style="font-size:3rem;">🎨</div>
                <div class="effect-label"><p>Classic Cartoon</p></div>
              </div>

              <div class="mockup-card side right">
                <div class="img-placeholder p3">⚡</div>
                <div class="effect-label"><p>Neon Glow</p></div>
              </div>
            </div>

            <h2>Turn photos into<br><span class="gradient-text">AI masterpieces</span></h2>
            <p class="subtitle">10 powerful effects. Instant results.<br>No skills needed.</p>

            <!-- 10 effect chips -->
            <div class="effects-grid">
              <div class="effect-chip"><span class="emoji">🎨</span><span class="name">Cartoon</span></div>
              <div class="effect-chip"><span class="emoji">🌊</span><span class="name">Water</span></div>
              <div class="effect-chip"><span class="emoji">⚡</span><span class="name">Neon</span></div>
              <div class="effect-chip"><span class="emoji">✏️</span><span class="name">Sketch</span></div>
              <div class="effect-chip"><span class="emoji">🖌️</span><span class="name">Oil</span></div>
              <div class="effect-chip"><span class="emoji">🕹️</span><span class="name">Pixel</span></div>
              <div class="effect-chip"><span class="emoji">📷</span><span class="name">Vintage</span></div>
              <div class="effect-chip"><span class="emoji">🌸</span><span class="name">Anime</span></div>
              <div class="effect-chip"><span class="emoji">💥</span><span class="name">Comic</span></div>
              <div class="effect-chip"><span class="emoji">🖍️</span><span class="name">Pencil</span></div>
            </div>

            <!-- Stats -->
            <div class="stat-row">
              <div class="stat-pill pill-green">
                <div class="dot dot-green"></div> Free Forever
              </div>
              <div class="stat-pill pill-purple">
                <div class="dot dot-purple"></div> 10 AI Effects
              </div>
              <div class="stat-pill pill-red">
                <div class="dot dot-red"></div> Instant
              </div>
            </div>
          </div>

          <div class="footer">Tooifny &nbsp;·&nbsp; AI Art Studio &nbsp;·&nbsp; v2.0</div>
        </body>
        </html>
        """, height=920, scrolling=False)


if __name__ == "__main__":
    st.set_page_config(
        page_title="Toonify – Sign In",
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