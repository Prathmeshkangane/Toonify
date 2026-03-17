import streamlit as st
import sys, os, uuid, io, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from PIL import Image
from backend.image_processor import EFFECTS, create_comparison, get_image_stats
from backend.auth import save_image_history

try:
    from utils.styles import back_button
except ImportError:
    def back_button(label, page):
        if st.button(f"← {label}", key="back_nav"):
            st.session_state["page"] = page
            st.rerun()

UPLOAD_DIR    = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "processed")
os.makedirs(UPLOAD_DIR,    exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


def _page_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Outfit:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

    html, body, .stApp { background:#06060E !important; }
    #MainMenu, footer, header[data-testid="stHeader"],
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] { display:none !important; }
    .block-container { padding: 24px 32px 48px !important; max-width: 1300px !important; }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(147,112,219,.04) !important;
        border: 1.5px dashed rgba(147,112,219,.25) !important;
        border-radius: 16px !important;
        padding: 12px !important;
        transition: all .2s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(147,112,219,.5) !important;
        background: rgba(147,112,219,.07) !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] {
        font-family: 'Outfit', sans-serif !important;
        color: rgba(255,255,255,.35) !important;
    }

    /* Slider */
    .stSlider [data-testid="stSlider"] div[role="slider"] {
        background: linear-gradient(135deg,#9370DB,#C471ED) !important;
        box-shadow: 0 0 12px rgba(147,112,219,.6) !important;
    }
    .stSlider [data-testid="stSlider"] > div > div {
        background: rgba(147,112,219,.3) !important;
    }

    /* Metric */
    [data-testid="stMetric"] {
        background: rgba(255,255,255,.025) !important;
        border: 1px solid rgba(255,255,255,.06) !important;
        border-radius: 12px !important;
        padding: 12px 14px !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Syne', sans-serif !important;
        color: #F0ECF8 !important;
        font-size: 1.1rem !important;
    }
    [data-testid="stMetricLabel"] {
        font-family: 'Space Mono', monospace !important;
        color: rgba(255,255,255,.3) !important;
        font-size: .56rem !important;
        text-transform: uppercase !important;
        letter-spacing: .1em !important;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg,#9370DB,#C471ED) !important;
        color: #fff !important; border: none !important;
        border-radius: 12px !important; height: 46px !important;
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

    /* Download button */
    .stDownloadButton > button {
        background: rgba(52,211,153,.06) !important;
        border: 1px solid rgba(52,211,153,.2) !important;
        color: #34D399 !important;
        border-radius: 12px !important;
        height: 46px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: .85rem !important;
        transition: all .18s ease !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(52,211,153,.1) !important;
        transform: translateY(-1px) !important;
    }

    /* Progress bar */
    .stProgress > div > div > div { background: linear-gradient(90deg,#9370DB,#C471ED) !important; border-radius: 99px !important; }
    .stProgress > div > div { background: rgba(255,255,255,.05) !important; border-radius: 99px !important; }

    /* Select slider */
    .stSlider label {
        font-family: 'Space Mono', monospace !important;
        color: rgba(255,255,255,.3) !important;
        font-size: .62rem !important;
        text-transform: uppercase !important;
        letter-spacing: .12em !important;
    }
    </style>
    """, unsafe_allow_html=True)


def _label(text, color="rgba(255,255,255,.2)"):
    st.markdown(
        f'<p style="font-family:Space Mono,monospace;font-size:.6rem;color:{color};'
        f'text-transform:uppercase;letter-spacing:.16em;margin:0 0 10px;">{text}</p>',
        unsafe_allow_html=True
    )


def show_image_processing():
    _page_styles()
    back_button("Back", "dashboard")
    user = st.session_state.get("user", {})

    # Page header
    st.markdown("""
    <div style="margin-bottom:32px;padding-bottom:20px;border-bottom:1px solid rgba(255,255,255,.05);">
      <p style="font-family:'Space Mono',monospace;font-size:.6rem;color:rgba(147,112,219,.6);
                text-transform:uppercase;letter-spacing:.18em;margin:0 0 8px;">Art Studio</p>
      <h2 style="font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;
                 color:#F0ECF8;margin:0;letter-spacing:-.05em;">Transform Your Photo</h2>
    </div>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 1.65])

    # ══ LEFT ══
    with left_col:
        # Upload section
        st.markdown("""
        <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.06);
                    border-radius:18px;padding:20px;margin-bottom:16px;">
          <p style="font-family:'Space Mono',monospace;font-size:.6rem;
                    color:rgba(147,112,219,.6);text-transform:uppercase;
                    letter-spacing:.14em;margin:0 0 14px;">01 · Upload Image</p>
        </div>
        """, unsafe_allow_html=True)

        _label("01 / Upload")
        uploaded = st.file_uploader(
            "Drop image here",
            type=["jpg","jpeg","png","bmp","webp"],
            label_visibility="visible"
        )

        if not uploaded:
            st.markdown("""
            <div style="background:rgba(147,112,219,.04);border:1px solid rgba(147,112,219,.1);
                        border-radius:14px;padding:16px 18px;margin-top:8px;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                <span style="font-size:1.1rem;">📁</span>
                <p style="font-family:'Syne',sans-serif;font-weight:600;font-size:.85rem;
                           color:rgba(255,255,255,.5);margin:0;">Supported Formats</p>
              </div>
              <p style="font-family:'Space Mono',monospace;font-size:.6rem;color:rgba(255,255,255,.25);
                        margin:0;line-height:1.8;">JPG / PNG / BMP / WebP<br>Max 10MB &nbsp;·&nbsp; 10 AI Effects</p>
            </div>
            """, unsafe_allow_html=True)
            return

        size_mb = len(uploaded.getvalue()) / (1024 * 1024)
        if size_mb > 10:
            st.error(f"File too large ({size_mb:.1f} MB). Max is 10 MB.")
            return
        try:
            pil_img = Image.open(uploaded).convert("RGB")
        except Exception:
            st.error("Could not read image. Try another file.")
            return

        fname     = f"orig_{uuid.uuid4().hex[:8]}_{uploaded.name}"
        orig_path = os.path.join(UPLOAD_DIR, fname)
        pil_img.save(orig_path)
        stats = get_image_stats(pil_img)

        # Image preview with styled container
        st.markdown("""
        <div style="border-radius:14px;overflow:hidden;border:1px solid rgba(255,255,255,.06);
                    margin-bottom:12px;">
        """, unsafe_allow_html=True)
        st.image(pil_img, caption="Original", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Image stats
        rows = "".join([
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:8px 0;{("border-bottom:1px solid rgba(255,255,255,.04);" if i < 3 else "")}">'
            f'<span style="font-family:Outfit,sans-serif;font-size:.8rem;color:rgba(255,255,255,.3);">{lbl}</span>'
            f'<span style="font-family:Space Mono,monospace;font-size:.75rem;color:#F0ECF8;">{val}</span></div>'
            for i, (lbl, val) in enumerate([
                ("Dimensions", f"{stats['width']} × {stats['height']}"),
                ("File size",  f"{size_mb:.2f} MB"),
                ("Brightness", str(stats["brightness"])),
                ("Contrast",   str(stats["contrast"])),
            ])
        ])
        st.markdown(f"""
        <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.06);
                    border-radius:14px;padding:14px 16px;margin-top:4px;">
          <p style="font-family:'Space Mono',monospace;font-size:.58rem;color:rgba(255,255,255,.2);
                    text-transform:uppercase;letter-spacing:.12em;margin:0 0 10px;">Image Info</p>
          {rows}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

        # Intensity selector
        _label("02 / Intensity", "rgba(147,112,219,.6)")
        st.markdown("""
        <p style="font-family:'Outfit',sans-serif;font-size:.78rem;color:rgba(255,255,255,.25);
                  margin:0 0 8px;">Adjust the effect strength</p>
        """, unsafe_allow_html=True)
        intensity = st.select_slider(
            "Intensity",
            options=["light","medium","strong"],
            value=st.session_state.get("intensity","medium"),
            key="intensity_slider",
            label_visibility="collapsed"
        )
        st.session_state["intensity"] = intensity

        # Visual intensity indicator
        int_colors = {"light": "#60A5FA", "medium": "#9370DB", "strong": "#F64F59"}
        int_pct = {"light": "33%", "medium": "66%", "strong": "100%"}
        st.markdown(f"""
        <div style="background:rgba(255,255,255,.04);border-radius:99px;height:4px;
                    margin:-2px 0 16px;overflow:hidden;">
          <div style="width:{int_pct[intensity]};height:100%;
                      background:{int_colors[intensity]};
                      box-shadow:0 0 8px {int_colors[intensity]};
                      border-radius:99px;transition:width .3s ease;"></div>
        </div>
        """, unsafe_allow_html=True)

        selected_style = st.session_state.get("selected_style", list(EFFECTS.keys())[0])
        effect_label   = selected_style.split(' ',1)[1] if ' ' in selected_style else selected_style
        _label("03 / Apply Effect", "rgba(52,211,153,.6)")
        apply_clicked = st.button(
            f"✨ Apply  {effect_label}",
            type="primary", use_container_width=True, key="apply_btn"
        )

        if apply_clicked:
            pb = st.progress(0, "Initializing...")
            for pct, msg in [(20,"Loading image..."),(50,"Applying effect..."),(80,"Finalizing...")]:
                time.sleep(0.15); pb.progress(pct, msg)
            try:
                result_img, elapsed = EFFECTS[selected_style]["fn"](pil_img, intensity)
            except Exception as e:
                st.error(f"Processing failed: {e}")
                return
            pb.progress(100, "Done! ✨"); time.sleep(0.25); pb.empty()

            proc_fname = f"proc_{uuid.uuid4().hex[:8]}.png"
            proc_path  = os.path.join(PROCESSED_DIR, proc_fname)
            result_img.save(proc_path)

            st.session_state.update({
                "result_img":     result_img,
                "result_style":   selected_style,
                "result_elapsed": elapsed,
                "proc_path":      proc_path,
                "orig_path":      orig_path,
            })
            for k in ["payment_verified","paid_order_id","paid_payment_id","payment_order"]:
                st.session_state.pop(k, None)

            if user.get("user_id"):
                save_image_history(user["user_id"], orig_path, proc_path, selected_style)

    # ══ RIGHT ══
    with right_col:
        # Effect selector
        _label("04 / Choose Effect", "rgba(147,112,219,.6)")
        effect_names   = list(EFFECTS.keys())
        selected_style = st.session_state.get("selected_style", effect_names[0])

        for row_start in [0, 5]:
            row_names = effect_names[row_start:row_start+5]
            cols      = st.columns(5)
            for col, name in zip(cols, row_names):
                info   = EFFECTS[name]
                is_sel = (name == selected_style)
                with col:
                    if is_sel:
                        st.markdown(f"""
                        <div style="background:linear-gradient(145deg,rgba(147,112,219,.15),rgba(196,113,237,.1));
                                    border:1px solid rgba(147,112,219,.45);
                                    border-radius:14px;padding:14px 6px;text-align:center;
                                    box-shadow:0 0 24px rgba(147,112,219,.15);">
                          <div style="font-size:1.4rem;margin-bottom:6px;">{info['icon']}</div>
                          <p style="font-family:'Space Mono',monospace;color:#C471ED;
                                    font-size:.56rem;font-weight:700;margin:0;line-height:1.3;
                                    text-transform:uppercase;letter-spacing:.04em;">
                            {name.split(' ',1)[1] if ' ' in name else name}
                          </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.06);
                                    border-radius:14px;padding:14px 6px;text-align:center;
                                    transition:all .2s ease;">
                          <div style="font-size:1.4rem;margin-bottom:6px;opacity:.45;">{info['icon']}</div>
                          <p style="font-family:'Space Mono',monospace;color:rgba(255,255,255,.25);
                                    font-size:.56rem;margin:0;line-height:1.3;
                                    text-transform:uppercase;letter-spacing:.04em;">
                            {name.split(' ',1)[1] if ' ' in name else name}
                          </p>
                        </div>
                        """, unsafe_allow_html=True)
                    if st.button("Select", key=f"sel_{name}", use_container_width=True):
                        st.session_state["selected_style"] = name
                        st.rerun()
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Selected effect description
        sel_info = EFFECTS[selected_style]
        icon = selected_style.split(' ', 1)[0] if ' ' in selected_style else ''
        st.markdown(f"""
        <div style="background:rgba(147,112,219,.05);border:1px solid rgba(147,112,219,.18);
                    border-left:3px solid #9370DB;border-radius:12px;padding:14px 18px;
                    margin:14px 0;display:flex;align-items:center;gap:14px;">
          <span style="font-size:1.6rem;">{sel_info['icon']}</span>
          <div>
            <p style="font-family:'Syne',sans-serif;font-weight:700;color:#F0ECF8;
                      margin:0 0 3px;font-size:.9rem;">{selected_style}</p>
            <p style="font-family:'Outfit',sans-serif;color:rgba(255,255,255,.35);margin:0;font-size:.8rem;">{sel_info['desc']}</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Result area
        if "result_img" not in st.session_state:
            st.markdown("""
            <div style="background:#0A0A14;border:1px solid rgba(255,255,255,.05);
                        border-radius:18px;padding:40px;text-align:center;">
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;">
                <div>
                  <p style="font-family:'Space Mono',monospace;font-size:.57rem;
                             color:rgba(255,255,255,.2);text-transform:uppercase;
                             letter-spacing:.1em;margin:0 0 10px;">Before</p>
                  <div style="aspect-ratio:4/3;border-radius:12px;
                               background:rgba(255,255,255,.025);
                               border:1px dashed rgba(255,255,255,.07);
                               display:flex;align-items:center;justify-content:center;
                               font-size:1.8rem;opacity:.3;">📷</div>
                </div>
                <div>
                  <p style="font-family:'Space Mono',monospace;font-size:.57rem;
                             color:rgba(147,112,219,.5);text-transform:uppercase;
                             letter-spacing:.1em;margin:0 0 10px;">After</p>
                  <div style="aspect-ratio:4/3;border-radius:12px;
                               background:linear-gradient(145deg,rgba(147,112,219,.06),rgba(196,113,237,.04));
                               border:1px dashed rgba(147,112,219,.15);
                               display:flex;align-items:center;justify-content:center;
                               font-size:1.8rem;opacity:.5;">✨</div>
                </div>
              </div>
              <p style="font-family:'Outfit',sans-serif;font-size:.85rem;
                        color:rgba(255,255,255,.2);margin:0;">
                Upload an image, choose an effect, and click <strong style="color:#9370DB;">Apply</strong>
              </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            result_img   = st.session_state["result_img"]
            result_style = st.session_state.get("result_style","")
            elapsed      = st.session_state.get("result_elapsed",0)

            # Success banner
            st.markdown(f"""
            <div style="background:rgba(52,211,153,.05);border:1px solid rgba(52,211,153,.18);
                        border-radius:12px;padding:13px 18px;margin-bottom:16px;
                        display:flex;align-items:center;gap:12px;">
              <div style="width:32px;height:32px;border-radius:99px;
                          background:rgba(52,211,153,.12);border:1px solid rgba(52,211,153,.25);
                          display:flex;align-items:center;justify-content:center;
                          font-size:.9rem;">✓</div>
              <div>
                <p style="font-family:'Syne',sans-serif;color:#F0ECF8;font-weight:700;
                           margin:0;font-size:.88rem;">Effect applied successfully!</p>
                <p style="font-family:'Space Mono',monospace;color:rgba(255,255,255,.25);margin:0;
                           font-size:.6rem;">{result_style} &nbsp;·&nbsp; {elapsed}s processing time</p>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Before / After
            ba_l, ba_r = st.columns(2)
            with ba_l:
                st.markdown('<p style="font-family:Space Mono,monospace;color:rgba(255,255,255,.2);font-size:.58rem;'
                            'text-transform:uppercase;letter-spacing:.1em;margin-bottom:7px;">Before</p>',
                            unsafe_allow_html=True)
                st.image(pil_img, use_container_width=True)
            with ba_r:
                lbl = result_style.split(" ",1)[1] if " " in result_style else result_style
                st.markdown(f'<p style="font-family:Space Mono,monospace;color:rgba(147,112,219,.7);font-size:.58rem;'
                            f'text-transform:uppercase;letter-spacing:.1em;margin-bottom:7px;">{lbl}</p>',
                            unsafe_allow_html=True)
                st.image(result_img, use_container_width=True)

            # Stats row
            orig_s = get_image_stats(pil_img)
            proc_s = get_image_stats(result_img)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Original",   f"{orig_s['width']}×{orig_s['height']}")
            c2.metric("Output",     f"{proc_s['width']}×{proc_s['height']}")
            c3.metric("Brightness", f"{proc_s['brightness'] - orig_s['brightness']:+.1f}")
            c4.metric("Time",       f"{elapsed}s")

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            # Action buttons
            dl1, dl2, dl3 = st.columns(3)
            with dl1:
                if st.button(
                    "⬇ Download  ·  ₹10",
                    type="primary", use_container_width=True, key="go_payment_btn",
                ):
                    st.session_state["page"] = "payment"
                    st.rerun()

            with dl2:
                comp = create_comparison(pil_img, result_img, result_style)
                cbuf = io.BytesIO(); comp.save(cbuf, "PNG")
                st.download_button(
                    "↔ Free Preview",
                    cbuf.getvalue(),
                    file_name="preview_comparison.png",
                    mime="image/png",
                    use_container_width=True,
                    key="free_preview_dl",
                )

            with dl3:
                if st.button("↺ Try Another", use_container_width=True, key="retry_btn"):
                    for k in ["result_img","result_style","result_elapsed","proc_path"]:
                        st.session_state.pop(k, None)
                    st.rerun()

            # Upsell
            st.markdown("""
            <div style="background:rgba(147,112,219,.04);border:1px solid rgba(147,112,219,.1);
                        border-radius:12px;padding:12px 16px;margin-top:8px;
                        display:flex;align-items:center;gap:12px;">
              <span style="font-size:1rem;">💎</span>
              <p style="font-family:'Outfit',sans-serif;font-size:.78rem;color:rgba(255,255,255,.35);margin:0;">
                Pay <strong style="color:#9370DB;">₹10</strong> to unlock full-resolution PNG &amp; JPG,
                zero watermarks, re-download anytime.
              </p>
            </div>
            """, unsafe_allow_html=True)