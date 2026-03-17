import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import streamlit.components.v1 as components

try:
    from backend.auth import register_user, validate_email, validate_password, password_strength
except ImportError:
    def validate_email(e): return "@" in e and "." in e.split("@")[-1]
    def validate_password(p):
        if len(p) < 8: return False, "Password must be at least 8 characters"
        return True, ""
    def password_strength(p):
        score = 0
        if len(p) >= 8: score += 1
        if any(c.isupper() for c in p): score += 1
        if any(c.islower() for c in p): score += 1
        if any(c.isdigit() for c in p): score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in p): score += 1
        return score
    def register_user(username, email, password):
        return {"success": True, "user": {"username": username}}


def show_register_page():

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Outfit:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

    html, body, .stApp { margin:0 !important; padding:0 !important; background:#06060E !important; overflow-x:hidden !important; }
    #MainMenu, footer, header[data-testid="stHeader"],
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] { display:none !important; }
    .block-container { padding:0 !important; max-width:100% !important; }
    section[data-testid="stMain"] > div { padding:0 !important; }
    [data-testid="column"] { padding:0 !important; gap:0 !important; }
    .stHorizontalBlock { gap:0 !important; }

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
        box-shadow: 0 4px 30px rgba(147,112,219,.3) !important;
        transition: all .25s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 40px rgba(147,112,219,.45) !important;
    }
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
    .stCheckbox label span {
        color: rgba(255,255,255,.4) !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: .83rem !important;
    }
    .stSuccess { background: rgba(52,211,153,.06) !important; border:1px solid rgba(52,211,153,.2) !important; border-radius:12px !important; }
    .stError   { background: rgba(246,79,89,.06) !important; border:1px solid rgba(246,79,89,.18) !important; border-radius:12px !important; }
    [data-testid="stAlert"] { font-family:'Outfit',sans-serif !important; font-size:.875rem !important; border-left-width:0 !important; color:#F0ECF8 !important; }
    .stSpinner > div { border-top-color: #9370DB !important; }
    iframe { border: none !important; display: block !important; }
    </style>
    """, unsafe_allow_html=True)

    left, right = st.columns([9, 11])

    # ════════════ LEFT — form side ════════════
    with left:
        # Logo bar
        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:40px 60px 0;margin-bottom:44px;">
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
                         color:#F0ECF8;letter-spacing:-.03em;">CartoonizeMe</span>
          </div>
          <div style="font-family:'Outfit',sans-serif;font-size:.82rem;color:rgba(255,255,255,.25);">
            Have account?&nbsp;<span style="color:#C471ED;font-weight:600;cursor:pointer;">Sign in &#x2197;</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Heading
        st.markdown("""
        <div style="padding:0 60px;margin-bottom:22px;">
          <div style="display:inline-flex;align-items:center;gap:7px;
                      background:rgba(52,211,153,.06);border:1px solid rgba(52,211,153,.14);
                      border-radius:99px;padding:4px 13px;margin-bottom:18px;">
            <div style="width:5px;height:5px;border-radius:50%;background:#34D399;
                        box-shadow:0 0 8px rgba(52,211,153,.9);"></div>
            <span style="font-family:'Space Mono',monospace;font-size:.6rem;
                         color:#34D399;letter-spacing:.12em;text-transform:uppercase;">Free Forever</span>
          </div>
          <h1 style="font-family:'Syne',sans-serif;font-weight:800;font-size:2.4rem;
                     color:#F0ECF8;margin:0 0 10px;letter-spacing:-.05em;line-height:1.1;">
            Create your<br>
            <span style="background:linear-gradient(135deg,#9370DB,#C471ED,#F64F59);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                         background-clip:text;">account.</span>
          </h1>
          <p style="font-family:'Outfit',sans-serif;font-size:.9rem;
                    color:rgba(255,255,255,.3);margin:0;line-height:1.65;">
            Start turning your photos into AI art today
          </p>
        </div>
        """, unsafe_allow_html=True)

        _, fc, _ = st.columns([60, 999, 60])
        with fc:
            username = st.text_input("Username", placeholder="Choose a username", key="reg_uname")
            if username:
                if len(username) >= 3:
                    st.markdown('<p style="font-family:\'Space Mono\',monospace;font-size:.65rem;'
                                'color:#34D399;margin:-4px 0 10px;letter-spacing:.05em;">'
                                '&#10003; Valid username</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p style="font-family:\'Space Mono\',monospace;font-size:.65rem;'
                                'color:#F64F59;margin:-4px 0 10px;letter-spacing:.05em;">'
                                '&#10005; Min 3 characters</p>', unsafe_allow_html=True)

            email = st.text_input("Email", placeholder="your@email.com", key="reg_email")
            if email:
                if validate_email(email):
                    st.markdown('<p style="font-family:\'Space Mono\',monospace;font-size:.65rem;'
                                'color:#34D399;margin:-4px 0 10px;letter-spacing:.05em;">'
                                '&#10003; Valid email</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p style="font-family:\'Space Mono\',monospace;font-size:.65rem;'
                                'color:#F64F59;margin:-4px 0 10px;letter-spacing:.05em;">'
                                '&#10005; Invalid format</p>', unsafe_allow_html=True)

            show_pw = st.checkbox("Show password", key="reg_show")
            pt = "default" if show_pw else "password"

            password = st.text_input("Password", type=pt, placeholder="Create a strong password", key="reg_pw")

            # Password strength meter
            if password:
                score  = password_strength(password)
                colors = ["#F64F59", "#FBBF24", "#FBBF24", "#34D399", "#9370DB"]
                labels = ["Very Weak", "Weak", "Fair", "Strong", "Very Strong"]
                sc     = max(score - 1, 0)
                segs   = "".join([
                    f'<div style="flex:1;height:3px;border-radius:99px;'
                    f'background:{colors[sc] if i < score else "rgba(255,255,255,.05)"}"></div>'
                    for i in range(5)
                ])
                has_up  = any(c.isupper() for c in password)
                has_lo  = any(c.islower() for c in password)
                has_di  = any(c.isdigit() for c in password)
                has_sp  = any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password)
                has_len = len(password) >= 8

                def cr(ok, t):
                    c = "#34D399" if ok else "rgba(255,255,255,.18)"
                    i = "&#10003;" if ok else "&#8729;"
                    return (f'<span style="font-family:\'Space Mono\',monospace;font-size:.6rem;'
                            f'color:{c};margin-right:10px;">{i} {t}</span>')

                crit = cr(has_len,"8+ chars") + cr(has_up,"Upper") + cr(has_lo,"Lower") + cr(has_di,"Number") + cr(has_sp,"Symbol")
                st.markdown(
                    f'<div style="margin:4px 0 14px;">'
                    f'<div style="display:flex;gap:3px;margin-bottom:6px;">{segs}</div>'
                    f'<span style="font-family:\'Space Mono\',monospace;font-size:.62rem;color:{colors[sc]};'
                    f'text-transform:uppercase;font-weight:700;letter-spacing:.08em;">{labels[sc]}</span>'
                    f'<div style="margin-top:6px;display:flex;flex-wrap:wrap;">{crit}</div></div>',
                    unsafe_allow_html=True
                )

            confirm = st.text_input("Confirm Password", type=pt, placeholder="Repeat your password", key="reg_cpw")
            if confirm and password:
                if password == confirm:
                    st.markdown('<p style="font-family:\'Space Mono\',monospace;font-size:.65rem;'
                                'color:#34D399;margin:-4px 0 10px;letter-spacing:.05em;">'
                                '&#10003; Passwords match</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p style="font-family:\'Space Mono\',monospace;font-size:.65rem;'
                                'color:#F64F59;margin:-4px 0 10px;letter-spacing:.05em;">'
                                '&#10005; Passwords do not match</p>', unsafe_allow_html=True)

            terms = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="reg_terms")

            # Inline validation errors
            errors = []
            if email and not validate_email(email):           errors.append("Invalid email format")
            if password and confirm and password != confirm:  errors.append("Passwords do not match")
            if password:
                ok, msg = validate_password(password)
                if not ok: errors.append(msg)
            for e in errors:
                st.markdown(
                    f'<div style="background:rgba(246,79,89,.05);border:1px solid rgba(246,79,89,.15);'
                    f'border-radius:10px;padding:8px 14px;margin:3px 0;">'
                    f'<span style="color:#F64F59;font-size:.8rem;font-family:\'Outfit\',sans-serif;">'
                    f'&#10005; {e}</span></div>',
                    unsafe_allow_html=True
                )

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            if st.button("Create My Account →", use_container_width=True, type="primary", key="reg_submit"):
                if not username or not email or not password or not confirm:
                    st.error("Please fill in all fields.")
                elif not terms:
                    st.error("Please accept the Terms of Service.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                elif errors:
                    st.error("Please fix the errors above.")
                else:
                    with st.spinner("Creating your account..."):
                        result = register_user(username, email, password)
                    if result["success"]:
                        st.success("Account created! Redirecting…")
                        st.balloons()
                        import time; time.sleep(1.2)
                        st.session_state["page"] = "login"
                        st.rerun()
                    else:
                        st.error(result["message"])

            st.markdown("""
            <div style="display:flex;align-items:center;gap:14px;margin:22px 0 18px;">
              <div style="flex:1;height:1px;background:rgba(255,255,255,.06);"></div>
              <span style="font-family:'Space Mono',monospace;font-size:.6rem;
                           color:rgba(255,255,255,.18);letter-spacing:.12em;
                           text-transform:uppercase;white-space:nowrap;">Already a member?</span>
              <div style="flex:1;height:1px;background:rgba(255,255,255,.06);"></div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Sign In Instead", use_container_width=True, key="go_login"):
                st.session_state["page"] = "login"
                st.rerun()

        st.markdown("""
        <div style="padding:16px 60px 32px;background:#06060E;
                    border-right:1px solid rgba(255,255,255,.04);">
          <p style="font-family:'Outfit',sans-serif;font-size:.73rem;
                    color:rgba(255,255,255,.15);line-height:1.7;margin:0;">
            By creating an account you agree to our
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
          .orb { position: absolute; border-radius: 50%; pointer-events: none; }
          .orb-1 { top: -120px; right: -80px; width: 500px; height: 500px;
                   background: radial-gradient(circle, rgba(147,112,219,.14) 0%, transparent 65%); }
          .orb-2 { bottom: -100px; left: -60px; width: 440px; height: 440px;
                   background: radial-gradient(circle, rgba(246,79,89,.1) 0%, transparent 65%); }
          .orb-3 { top: 35%; right: 5%; width: 280px; height: 280px;
                   background: radial-gradient(circle, rgba(52,211,153,.06) 0%, transparent 65%); }

          .content {
            position: relative; z-index: 2;
            text-align: center; max-width: 420px; width: 100%;
            animation: fadeUp .7s ease both;
          }
          .icon-wrap {
            display: inline-flex; align-items: center; justify-content: center;
            width: 68px; height: 68px; border-radius: 20px; margin-bottom: 28px;
            background: linear-gradient(135deg, #9370DB, #C471ED);
            box-shadow: 0 0 0 12px rgba(147,112,219,.06), 0 10px 40px rgba(147,112,219,.5);
            animation: iconPulse 3s ease-in-out infinite;
          }
          h2 {
            font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1.9rem;
            color: #F0ECF8; margin: 0 0 12px; letter-spacing: -.04em; line-height: 1.15;
          }
          .gradient-text {
            background: linear-gradient(135deg, #9370DB, #C471ED, #F64F59);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
          }
          .subtitle {
            font-size: .87rem; color: rgba(255,255,255,.3);
            margin: 0 0 40px; line-height: 1.7;
          }

          /* Steps */
          .steps { display: flex; flex-direction: column; gap: 10px; margin-bottom: 36px; text-align: left; }
          .step {
            display: flex; align-items: center; gap: 16px;
            background: rgba(255,255,255,.025);
            border: 1px solid rgba(255,255,255,.06);
            border-radius: 16px; padding: 16px 20px;
            transition: all .25s ease;
            animation: fadeUp .5s ease both;
          }
          .step:nth-child(1) { animation-delay: .1s; }
          .step:nth-child(2) { animation-delay: .2s; }
          .step:nth-child(3) { animation-delay: .3s; }
          .step:hover {
            border-color: rgba(147,112,219,.22);
            background: rgba(147,112,219,.04);
            transform: translateX(5px);
          }
          .step-num {
            flex-shrink: 0;
            width: 32px; height: 32px; border-radius: 10px;
            background: linear-gradient(135deg, rgba(147,112,219,.2), rgba(196,113,237,.12));
            border: 1px solid rgba(147,112,219,.25);
            display: flex; align-items: center; justify-content: center;
            font-family: 'Space Mono', sans-serif; font-weight: 700; font-size: .68rem;
            color: #C471ED;
          }
          .step-title {
            font-family: 'Syne', sans-serif; font-weight: 700; font-size: .88rem;
            color: #F0ECF8; margin: 0 0 2px;
          }
          .step-desc {
            font-size: .76rem; color: rgba(255,255,255,.28); margin: 0; line-height: 1.5;
          }

          /* Stats */
          .stats { display: flex; align-items: center; justify-content: center; gap: 8px; flex-wrap: wrap; }
          .stat-pill {
            display: flex; align-items: center; gap: 6px;
            border-radius: 99px; padding: 5px 13px;
            font-size: .73rem; font-weight: 500; color: rgba(255,255,255,.4);
          }
          .pill-g { background: rgba(52,211,153,.05); border: 1px solid rgba(52,211,153,.14); }
          .pill-p { background: rgba(147,112,219,.05); border: 1px solid rgba(147,112,219,.14); }
          .pill-r { background: rgba(246,79,89,.05); border: 1px solid rgba(246,79,89,.14); }
          .dot { width: 5px; height: 5px; border-radius: 50%; }
          .dot-g { background: #34D399; box-shadow: 0 0 7px rgba(52,211,153,.9); }
          .dot-p { background: #9370DB; box-shadow: 0 0 7px rgba(147,112,219,.9); }
          .dot-r { background: #F64F59; box-shadow: 0 0 7px rgba(246,79,89,.9); }

          .footer {
            position: absolute; bottom: 20px; text-align: center;
            z-index: 2; width: 100%;
            font-family: 'Space Mono', monospace;
            font-size: .58rem; color: rgba(255,255,255,.1);
            letter-spacing: .14em; text-transform: uppercase;
          }

          @keyframes fadeUp {
            from { opacity: 0; transform: translateY(24px); }
            to   { opacity: 1; transform: translateY(0); }
          }
          @keyframes iconPulse {
            0%, 100% { box-shadow: 0 0 0 12px rgba(147,112,219,.06), 0 10px 40px rgba(147,112,219,.5); }
            50% { box-shadow: 0 0 0 18px rgba(147,112,219,.04), 0 10px 50px rgba(147,112,219,.65); }
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
            <div class="icon-wrap">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                      stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>

            <h2>Three steps to<br><span class="gradient-text">your first artwork</span></h2>
            <p class="subtitle">No design skills needed.<br>Just upload, pick a style, and download.</p>

            <div class="steps">
              <div class="step">
                <div class="step-num">01</div>
                <div>
                  <p class="step-title">Upload your photo</p>
                  <p class="step-desc">Any portrait, selfie, or image — JPG, PNG, WebP</p>
                </div>
              </div>
              <div class="step">
                <div class="step-num">02</div>
                <div>
                  <p class="step-title">Choose an AI style</p>
                  <p class="step-desc">10 unique effects from cartoon to neon glow</p>
                </div>
              </div>
              <div class="step">
                <div class="step-num">03</div>
                <div>
                  <p class="step-title">Download &amp; share</p>
                  <p class="step-desc">Full resolution, no watermarks, yours forever</p>
                </div>
              </div>
            </div>

            <div class="stats">
              <div class="stat-pill pill-g"><div class="dot dot-g"></div> Free forever</div>
              <div class="stat-pill pill-p"><div class="dot dot-p"></div> 10 AI styles</div>
              <div class="stat-pill pill-r"><div class="dot dot-r"></div> No watermarks</div>
            </div>
          </div>

          <div class="footer">CartoonizeMe &nbsp;·&nbsp; AI Art Studio &nbsp;·&nbsp; v2.0</div>
        </body>
        </html>
        """, height=920, scrolling=False)


if __name__ == "__main__":
    st.set_page_config(
        page_title="CartoonizeMe – Create Account",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    if "page" not in st.session_state:
        st.session_state["page"] = "register"
    if st.session_state["page"] == "register":
        show_register_page()
    elif st.session_state["page"] == "login":
        st.write("→ Redirected to login page")