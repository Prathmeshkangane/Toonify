import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit.components.v1 as components

try:
    from backend.auth import register_user, validate_email, validate_password, password_strength
except ImportError:
    # ── stubs so the file runs standalone ──
    def validate_email(e):
        return "@" in e and "." in e.split("@")[-1]
    def validate_password(p):
        if len(p) < 8:
            return False, "Password must be at least 8 characters"
        return True, ""
    def password_strength(p):
        score = 0
        if len(p) >= 8:           score += 1
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
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap');

    html, body, .stApp { margin:0 !important; padding:0 !important; background:#08080F !important; overflow-x:hidden !important; }
    #MainMenu, footer, header[data-testid="stHeader"],
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"]                     { display:none !important; }
    .block-container                                   { padding:0 !important; max-width:100% !important; }
    section[data-testid="stMain"] > div                { padding:0 !important; }
    [data-testid="column"]                             { padding:0 !important; gap:0 !important; }
    .stHorizontalBlock                                 { gap:0 !important; }

    /* ── inputs ── */
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

    /* ── primary button ── */
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

    /* ── secondary button ── */
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

    /* ── checkbox ── */
    .stCheckbox label span {
        color: rgba(255,255,255,.45) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: .85rem !important;
    }

    /* ── alerts ── */
    .stSuccess { background: rgba(52,211,153,.07) !important; border:1px solid rgba(52,211,153,.25) !important; border-radius:10px !important; }
    .stError   { background: rgba(244,114,182,.07) !important; border:1px solid rgba(244,114,182,.22) !important; border-radius:10px !important; }
    [data-testid="stAlert"] { font-family:'DM Sans',sans-serif !important; font-size:.875rem !important; border-left-width:0 !important; color:#EEEAF8 !important; }
    .stSpinner > div { border-top-color: #A78BFA !important; }

    iframe { border: none !important; display: block !important; }
    </style>
    """, unsafe_allow_html=True)

    left, right = st.columns([9, 11])

    # ════════════════════════════════════════
    # LEFT — form side
    # ════════════════════════════════════════
    with left:
        # ── top nav + heading ──
        st.markdown("""
        <div style="background:#08080F;padding:40px 56px 24px 56px;
                    border-right:1px solid rgba(255,255,255,.05);box-sizing:border-box;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:44px;">
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
              Have an account?&nbsp;<span style="color:#A78BFA;font-weight:500;cursor:pointer;">Sign in</span>
            </span>
          </div>

          <div style="margin-bottom:22px;">
            <div style="display:inline-flex;align-items:center;gap:8px;
                        background:rgba(167,139,250,.08);border:1px solid rgba(167,139,250,.18);
                        border-radius:99px;padding:5px 14px;margin-bottom:18px;">
              <div style="width:6px;height:6px;border-radius:50%;background:#A78BFA;
                          box-shadow:0 0 8px rgba(167,139,250,.8);"></div>
              <span style="font-family:'DM Sans',sans-serif;font-size:.72rem;font-weight:600;
                           color:#A78BFA;letter-spacing:.08em;text-transform:uppercase;">Free Forever</span>
            </div>
            <h1 style="font-family:'Syne',sans-serif;font-weight:800;font-size:2.2rem;
                       color:#EEEAF8;margin:0 0 10px;letter-spacing:-.04em;line-height:1.15;">
              Create account
            </h1>
            <p style="font-family:'DM Sans',sans-serif;font-size:.9rem;
                      color:rgba(255,255,255,.35);margin:0;line-height:1.6;">
              Start turning your photos into AI art today
            </p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── form fields ──
        _, fc, _ = st.columns([56, 999, 56])
        with fc:

            username = st.text_input("Username", placeholder="Choose a username", key="reg_uname")
            if username:
                if len(username) >= 3:
                    st.markdown('<p style="font-family:\'DM Sans\',sans-serif;font-size:.72rem;'
                                'color:#34D399;margin:-6px 0 8px;letter-spacing:.03em;">'
                                '&#10003; Valid username</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p style="font-family:\'DM Sans\',sans-serif;font-size:.72rem;'
                                'color:#F472B6;margin:-6px 0 8px;letter-spacing:.03em;">'
                                '&#10005; At least 3 characters</p>', unsafe_allow_html=True)

            email = st.text_input("Email", placeholder="your@email.com", key="reg_email")
            if email:
                if validate_email(email):
                    st.markdown('<p style="font-family:\'DM Sans\',sans-serif;font-size:.72rem;'
                                'color:#34D399;margin:-6px 0 8px;letter-spacing:.03em;">'
                                '&#10003; Valid email</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p style="font-family:\'DM Sans\',sans-serif;font-size:.72rem;'
                                'color:#F472B6;margin:-6px 0 8px;letter-spacing:.03em;">'
                                '&#10005; Invalid email format</p>', unsafe_allow_html=True)

            show_pw = st.checkbox("Show password", key="reg_show")
            pt = "default" if show_pw else "password"

            password = st.text_input("Password", type=pt, placeholder="Create a strong password", key="reg_pw")

            # ── password strength meter ──
            if password:
                score  = password_strength(password)
                colors = ["#F472B6", "#FBBF24", "#FBBF24", "#34D399", "#A78BFA"]
                labels = ["Very Weak", "Weak", "Fair", "Strong", "Very Strong"]
                sc     = max(score - 1, 0)
                segs   = "".join([
                    f'<div style="flex:1;height:3px;border-radius:99px;'
                    f'background:{colors[sc] if i < score else "rgba(255,255,255,.06)"}"></div>'
                    for i in range(5)
                ])
                has_up  = any(c.isupper() for c in password)
                has_lo  = any(c.islower() for c in password)
                has_di  = any(c.isdigit() for c in password)
                has_sp  = any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password)
                has_len = len(password) >= 8

                def cr(ok, t):
                    c = "#34D399" if ok else "rgba(255,255,255,.2)"
                    i = "&#10003;" if ok else "&#8729;"
                    return (f'<span style="font-family:\'DM Sans\',sans-serif;font-size:.67rem;'
                            f'color:{c};margin-right:10px;">{i} {t}</span>')

                crit = cr(has_len,"8+ chars") + cr(has_up,"Upper") + cr(has_lo,"Lower") + cr(has_di,"Number") + cr(has_sp,"Symbol")
                st.markdown(
                    f'<div style="margin:4px 0 12px;">'
                    f'<div style="display:flex;gap:3px;margin-bottom:5px;">{segs}</div>'
                    f'<span style="font-family:\'DM Sans\',sans-serif;font-size:.67rem;color:{colors[sc]};'
                    f'text-transform:uppercase;font-weight:600;letter-spacing:.06em;">{labels[sc]}</span>'
                    f'<div style="margin-top:5px;display:flex;flex-wrap:wrap;">{crit}</div></div>',
                    unsafe_allow_html=True
                )

            confirm = st.text_input("Confirm Password", type=pt, placeholder="Repeat your password", key="reg_cpw")
            if confirm and password:
                if password == confirm:
                    st.markdown('<p style="font-family:\'DM Sans\',sans-serif;font-size:.72rem;'
                                'color:#34D399;margin:-6px 0 8px;letter-spacing:.03em;">'
                                '&#10003; Passwords match</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p style="font-family:\'DM Sans\',sans-serif;font-size:.72rem;'
                                'color:#F472B6;margin:-6px 0 8px;letter-spacing:.03em;">'
                                '&#10005; Passwords do not match</p>', unsafe_allow_html=True)

            terms = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="reg_terms")

            # ── inline validation errors ──
            errors = []
            if email and not validate_email(email):           errors.append("Invalid email format")
            if password and confirm and password != confirm:  errors.append("Passwords do not match")
            if password:
                ok, msg = validate_password(password)
                if not ok: errors.append(msg)
            for e in errors:
                st.markdown(
                    f'<div style="background:rgba(244,114,182,.06);border:1px solid rgba(244,114,182,.2);'
                    f'border-radius:8px;padding:8px 14px;margin:3px 0;">'
                    f'<span style="color:#F472B6;font-size:.8rem;font-family:\'DM Sans\',sans-serif;">'
                    f'&#10005; {e}</span></div>',
                    unsafe_allow_html=True
                )

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            if st.button("Create My Account", use_container_width=True, type="primary", key="reg_submit"):
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
            <div style="display:flex;align-items:center;gap:12px;margin:18px 0 14px;">
              <div style="flex:1;height:1px;background:rgba(255,255,255,.07);"></div>
              <span style="font-family:'DM Sans',sans-serif;font-size:.72rem;
                           color:rgba(255,255,255,.22);letter-spacing:.08em;
                           text-transform:uppercase;white-space:nowrap;">Already a member?</span>
              <div style="flex:1;height:1px;background:rgba(255,255,255,.07);"></div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Sign In Instead", use_container_width=True, key="go_login"):
                st.session_state["page"] = "login"
                st.rerun()

        st.markdown("""
        <div style="padding:16px 56px 32px;background:#08080F;
                    border-right:1px solid rgba(255,255,255,.05);">
          <p style="font-family:'DM Sans',sans-serif;font-size:.75rem;
                    color:rgba(255,255,255,.18);line-height:1.7;margin:0;">
            By creating an account you agree to our
            <span style="color:rgba(255,255,255,.38);text-decoration:underline;cursor:pointer;">Terms of Service</span>
            and
            <span style="color:rgba(255,255,255,.38);text-decoration:underline;cursor:pointer;">Privacy Policy</span>.
          </p>
        </div>
        """, unsafe_allow_html=True)

    # ════════════════════════════════════════
    # RIGHT — decorative panel via iframe
    # ════════════════════════════════════════
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
          .orb-1 { top: -80px;  right: -60px;  width: 460px; height: 460px;
                   background: radial-gradient(circle, rgba(167,139,250,.2) 0%, transparent 60%); }
          .orb-2 { bottom: -80px; left: -80px; width: 420px; height: 420px;
                   background: radial-gradient(circle, rgba(244,114,182,.15) 0%, transparent 60%); }
          .orb-3 { top: 40%; left: 10%; width: 300px; height: 300px;
                   background: radial-gradient(circle, rgba(96,165,250,.07) 0%, transparent 65%); }

          .grid {
            position: absolute; inset: 0; pointer-events: none;
            background-image: radial-gradient(rgba(255,255,255,.07) 1px, transparent 1px);
            background-size: 28px 28px;
          }
          .top-line {
            position: absolute; top: 0; left: 0; right: 0; height: 1px;
            background: linear-gradient(90deg, transparent, #A78BFA 40%, #F472B6 60%, transparent);
            opacity: .6;
          }

          /* ── content ── */
          .content {
            position: relative; z-index: 2;
            text-align: center; max-width: 400px; width: 100%;
            animation: fadeUp .6s ease both;
          }

          .icon-wrap {
            display: inline-flex; align-items: center; justify-content: center;
            width: 64px; height: 64px; border-radius: 20px; margin-bottom: 28px;
            background: linear-gradient(135deg, #A78BFA, #F472B6);
            box-shadow: 0 0 0 10px rgba(167,139,250,.07), 0 8px 32px rgba(167,139,250,.45);
          }

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

          /* ── steps ── */
          .steps { display: flex; flex-direction: column; gap: 12px; margin-bottom: 38px; text-align: left; }
          .step {
            display: flex; align-items: flex-start; gap: 14px;
            background: rgba(255,255,255,.03);
            border: 1px solid rgba(255,255,255,.07);
            border-radius: 14px; padding: 16px 18px;
            backdrop-filter: blur(12px);
            transition: border-color .2s, background .2s, transform .2s;
            animation: fadeUp .5s ease both;
          }
          .step:nth-child(1) { animation-delay: .1s; }
          .step:nth-child(2) { animation-delay: .2s; }
          .step:nth-child(3) { animation-delay: .3s; }
          .step:hover {
            border-color: rgba(167,139,250,.25);
            background: rgba(167,139,250,.04);
            transform: translateX(4px);
          }
          .step-num {
            flex-shrink: 0;
            width: 28px; height: 28px; border-radius: 8px;
            background: linear-gradient(135deg, rgba(167,139,250,.25), rgba(244,114,182,.15));
            border: 1px solid rgba(167,139,250,.3);
            display: flex; align-items: center; justify-content: center;
            font-family: 'Syne', sans-serif; font-weight: 800; font-size: .72rem;
            color: #A78BFA;
          }
          .step-body {}
          .step-title {
            font-family: 'Syne', sans-serif; font-weight: 700; font-size: .85rem;
            color: #EEEAF8; margin: 0 0 3px;
          }
          .step-desc {
            font-size: .75rem; color: rgba(255,255,255,.3); margin: 0; line-height: 1.5;
          }

          /* ── stat pills ── */
          .stats { display: flex; align-items: center; justify-content: center; gap: 8px; flex-wrap: wrap; }
          .stat {
            display: flex; align-items: center; gap: 7px;
            border-radius: 99px; padding: 6px 14px;
            font-size: .75rem; font-weight: 600; color: rgba(255,255,255,.5);
          }
          .stat-1 { background: rgba(52,211,153,.06);  border: 1px solid rgba(52,211,153,.15); }
          .stat-2 { background: rgba(167,139,250,.06); border: 1px solid rgba(167,139,250,.15); }
          .stat-3 { background: rgba(244,114,182,.06); border: 1px solid rgba(244,114,182,.15); }
          .dot { width: 6px; height: 6px; border-radius: 50%; }
          .dot-g { background: #34D399; box-shadow: 0 0 7px rgba(52,211,153,.9); }
          .dot-p { background: #A78BFA; box-shadow: 0 0 7px rgba(167,139,250,.9); }
          .dot-k { background: #F472B6; box-shadow: 0 0 7px rgba(244,114,182,.9); }

          .footer {
            position: absolute; bottom: 24px; text-align: center; z-index: 2; width: 100%;
            font-size: .68rem; color: rgba(255,255,255,.12);
            letter-spacing: .18em; text-transform: uppercase;
            font-family: 'DM Sans', sans-serif;
          }

          @keyframes fadeUp {
            from { opacity: 0; transform: translateY(20px); }
            to   { opacity: 1; transform: translateY(0); }
          }
        </style>
        </head>
        <body>

          <div class="orb orb-1"></div>
          <div class="orb orb-2"></div>
          <div class="orb orb-3"></div>
          <div class="grid"></div>
          <div class="top-line"></div>

          <div class="content">

            <div class="icon-wrap">
              <svg width="30" height="30" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                      stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>

            <h2>
              Three steps to<br>
              <span class="gradient-text">your first artwork</span>
            </h2>
            <p class="subtitle">
              No design skills needed. Just upload,<br>pick a style, and download.
            </p>

            <div class="steps">
              <div class="step">
                <div class="step-num">01</div>
                <div class="step-body">
                  <p class="step-title">Upload your photo</p>
                  <p class="step-desc">Any portrait, selfie, or image — JPG, PNG, WebP accepted</p>
                </div>
              </div>
              <div class="step">
                <div class="step-num">02</div>
                <div class="step-body">
                  <p class="step-title">Choose an AI style</p>
                  <p class="step-desc">10 unique effects from cartoon to watercolor to neon glow</p>
                </div>
              </div>
              <div class="step">
                <div class="step-num">03</div>
                <div class="step-body">
                  <p class="step-title">Download &amp; share</p>
                  <p class="step-desc">Full resolution, no watermarks, yours to keep forever</p>
                </div>
              </div>
            </div>

            <div class="stats">
              <div class="stat stat-1">
                <div class="dot dot-g"></div>
                Free forever
              </div>
              <div class="stat stat-2">
                <div class="dot dot-p"></div>
                10 AI styles
              </div>
              <div class="stat stat-3">
                <div class="dot dot-k"></div>
                No watermarks
              </div>
            </div>

          </div>

          <div class="footer">CartoonizeMe · AI Art Studio · v2.0</div>

        </body>
        </html>
        """, height=920, scrolling=False)


# ── entrypoint ──────────────────────────────────────────────
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