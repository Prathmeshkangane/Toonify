import streamlit as st
import sys, os, uuid, io, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from PIL import Image
from backend.image_processor import EFFECTS, create_comparison, get_image_stats
from backend.auth import save_image_history
from utils.styles import back_button

UPLOAD_DIR    = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "processed")
os.makedirs(UPLOAD_DIR,    exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


def _label(text):
    st.markdown(
        f'<p style="font-family:Syne Mono,monospace;font-size:.58rem;color:#3E3C58;'
        f'text-transform:uppercase;letter-spacing:.18em;margin:0 0 10px;">{text}</p>',
        unsafe_allow_html=True
    )


def show_image_processing():
    back_button("Back", "dashboard")
    user = st.session_state.get("user", {})

    st.markdown("""
    <div style="margin-bottom:28px;">
      <p style="font-family:'Syne Mono',monospace;font-size:.58rem;color:#3E3C58;
                text-transform:uppercase;letter-spacing:.18em;margin:0 0 8px;">Art Studio</p>
      <h2 style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
                 color:#EEEAF8;margin:0;letter-spacing:-.04em;">Transform Your Photo</h2>
    </div>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 1.65])

    # ══ LEFT ══
    with left_col:
        _label("01 / Upload")
        uploaded = st.file_uploader(
            "Drop image here",
            type=["jpg","jpeg","png","bmp","webp"],
            label_visibility="visible"
        )

        if not uploaded:
            st.markdown("""
            <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.06);
                        border-radius:12px;padding:14px 16px;margin-top:8px;">
              <p style="font-family:'Syne Mono',monospace;font-size:.6rem;color:#3E3C58;
                        margin:0 0 3px;letter-spacing:.06em;">JPG / PNG / BMP / WebP</p>
              <p style="font-family:'Syne Mono',monospace;font-size:.6rem;color:#3E3C58;
                        margin:0;">Max 10MB &nbsp;&#183;&nbsp; 10 Effects</p>
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

        st.image(pil_img, caption="Original", use_container_width=True)

        # Image info
        rows = "".join([
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:7px 0;border-bottom:1px solid rgba(255,255,255,.04);">'
            f'<span style="font-family:Outfit,sans-serif;font-size:.8rem;color:#7C7A9A;">{lbl}</span>'
            f'<span style="font-family:Syne Mono,monospace;font-size:.75rem;color:#EEEAF8;">{val}</span></div>'
            for lbl, val in [
                ("Dimensions", f"{stats['width']} x {stats['height']}"),
                ("File size",  f"{size_mb:.2f} MB"),
                ("Brightness", str(stats["brightness"])),
                ("Contrast",   str(stats["contrast"])),
            ]
        ])
        st.markdown(f"""
        <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.06);
                    border-radius:12px;padding:14px;margin-top:10px;">
          <p style="font-family:'Syne Mono',monospace;font-size:.58rem;color:#3E3C58;
                    text-transform:uppercase;letter-spacing:.12em;margin:0 0 10px;">Image Info</p>
          {rows}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        _label("02 / Intensity")
        intensity = st.select_slider(
            "Intensity",
            options=["light","medium","strong"],
            value=st.session_state.get("intensity","medium"),
            key="intensity_slider",
            label_visibility="collapsed"
        )
        st.session_state["intensity"] = intensity

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        selected_style = st.session_state.get("selected_style", list(EFFECTS.keys())[0])
        effect_label   = selected_style.split(' ',1)[1] if ' ' in selected_style else selected_style
        _label("03 / Apply")
        apply_clicked = st.button(
            f"Apply  {effect_label}",
            type="primary", use_container_width=True, key="apply_btn"
        )

        if apply_clicked:
            pb = st.progress(0, "Starting...")
            for pct, msg in [(20,"Loading image..."),(50,"Applying effect..."),(80,"Finishing up...")]:
                time.sleep(0.15); pb.progress(pct, msg)
            try:
                result_img, elapsed = EFFECTS[selected_style]["fn"](pil_img, intensity)
            except Exception as e:
                st.error(f"Processing failed: {e}")
                return
            pb.progress(100, "Done!"); time.sleep(0.2); pb.empty()

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
            # Clear any previous payment state when a new image is processed
            for k in ["payment_verified","paid_order_id","paid_payment_id","payment_order"]:
                st.session_state.pop(k, None)

            if user.get("user_id"):
                save_image_history(user["user_id"], orig_path, proc_path, selected_style)

    # ══ RIGHT ══
    with right_col:
        _label("04 / Choose Effect")
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
                        <div style="background:linear-gradient(135deg,rgba(167,139,250,.15),rgba(244,114,182,.1));
                                    border:1px solid rgba(167,139,250,.4);
                                    border-radius:12px;padding:12px 6px;text-align:center;
                                    box-shadow:0 0 20px rgba(167,139,250,.15);">
                          <div style="font-size:1.3rem;margin-bottom:5px;">{info['icon']}</div>
                          <p style="font-family:'Outfit',sans-serif;color:#A78BFA;
                                    font-size:.62rem;font-weight:700;margin:0;line-height:1.2;">
                            {name.split(' ',1)[1] if ' ' in name else name}
                          </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.06);
                                    border-radius:12px;padding:12px 6px;text-align:center;">
                          <div style="font-size:1.3rem;margin-bottom:5px;opacity:.5;">{info['icon']}</div>
                          <p style="font-family:'Outfit',sans-serif;color:#3E3C58;
                                    font-size:.62rem;margin:0;line-height:1.2;">
                            {name.split(' ',1)[1] if ' ' in name else name}
                          </p>
                        </div>
                        """, unsafe_allow_html=True)
                    if st.button("Pick", key=f"sel_{name}", use_container_width=True):
                        st.session_state["selected_style"] = name
                        st.rerun()
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        sel_info = EFFECTS[selected_style]
        st.markdown(f"""
        <div style="background:#0F0F18;border:1px solid rgba(167,139,250,.2);
                    border-left:3px solid #A78BFA;border-radius:10px;padding:12px 16px;
                    margin:12px 0;">
          <p style="font-family:'Syne',sans-serif;font-weight:700;color:#EEEAF8;
                    margin:0 0 3px;font-size:.88rem;">{selected_style}</p>
          <p style="font-family:'Outfit',sans-serif;color:#7C7A9A;margin:0;font-size:.8rem;">{sel_info['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

        if "result_img" not in st.session_state:
            st.markdown("""
            <div style="background:#0F0F18;border:1px solid rgba(255,255,255,.06);
                        border-radius:16px;padding:32px;text-align:center;">
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px;">
                <div>
                  <p style="font-family:'Syne Mono',monospace;font-size:.58rem;color:#3E3C58;
                             text-transform:uppercase;letter-spacing:.1em;margin:0 0 8px;">Before</p>
                  <div style="aspect-ratio:4/3;border-radius:10px;
                               background:#171723;border:1px solid rgba(255,255,255,.05);
                               display:flex;align-items:center;justify-content:center;">
                    <span style="font-size:1.5rem;opacity:.2;">&#128444;</span>
                  </div>
                </div>
                <div>
                  <p style="font-family:'Syne Mono',monospace;font-size:.58rem;color:#A78BFA;
                             text-transform:uppercase;letter-spacing:.1em;margin:0 0 8px;">After</p>
                  <div style="aspect-ratio:4/3;border-radius:10px;
                               background:linear-gradient(135deg,rgba(167,139,250,.06),rgba(244,114,182,.04));
                               border:1px solid rgba(167,139,250,.12);display:flex;
                               align-items:center;justify-content:center;">
                    <span style="font-size:1.5rem;opacity:.2;">&#10022;</span>
                  </div>
                </div>
              </div>
              <p style="font-family:'Outfit',sans-serif;font-size:.85rem;color:#3E3C58;margin:0;">
                Select an effect and click Apply
              </p>
            </div>
            """, unsafe_allow_html=True)

        else:
            result_img   = st.session_state["result_img"]
            result_style = st.session_state.get("result_style","")
            elapsed      = st.session_state.get("result_elapsed",0)

            st.markdown(f"""
            <div style="background:rgba(52,211,153,.05);border:1px solid rgba(52,211,153,.2);
                        border-radius:10px;padding:12px 16px;margin-bottom:14px;
                        display:flex;align-items:center;gap:12px;">
              <span style="color:#34D399;font-size:1.1rem;">&#10003;</span>
              <div>
                <p style="font-family:'Syne',sans-serif;color:#EEEAF8;font-weight:700;
                           margin:0;font-size:.88rem;">Effect applied!</p>
                <p style="font-family:'Syne Mono',monospace;color:#3E3C58;margin:0;
                           font-size:.62rem;">{result_style} &nbsp;&#183;&nbsp; {elapsed}s</p>
              </div>
            </div>
            """, unsafe_allow_html=True)

            ba_l, ba_r = st.columns(2)
            with ba_l:
                st.markdown('<p style="font-family:Syne Mono,monospace;color:#3E3C58;font-size:.6rem;'
                            'text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;">Before</p>',
                            unsafe_allow_html=True)
                st.image(pil_img, use_container_width=True)
            with ba_r:
                lbl = result_style.split(" ",1)[1] if " " in result_style else result_style
                st.markdown(f'<p style="font-family:Syne Mono,monospace;color:#A78BFA;font-size:.6rem;'
                            f'text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;">{lbl}</p>',
                            unsafe_allow_html=True)
                st.image(result_img, use_container_width=True)

            orig_s = get_image_stats(pil_img)
            proc_s = get_image_stats(result_img)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Original",     f"{orig_s['width']}x{orig_s['height']}")
            c2.metric("Output",       f"{proc_s['width']}x{proc_s['height']}")
            c3.metric("Brightness",   f"{proc_s['brightness'] - orig_s['brightness']:+.1f}")
            c4.metric("Time",         f"{elapsed}s")

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            # ── Action buttons (Download via payment + free comparison + retry) ──
            dl1, dl2, dl3 = st.columns(3)
            with dl1:
                # Primary CTA: pay to download full quality
                if st.button(
                    "⬇ Download  ·  ₹10",
                    type="primary",
                    use_container_width=True,
                    key="go_payment_btn",
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

            # Upsell nudge
            st.markdown("""
            <div style="background:rgba(167,139,250,.04);border:1px solid rgba(167,139,250,.12);
                        border-radius:10px;padding:10px 14px;margin-top:6px;
                        display:flex;align-items:center;gap:10px;">
              <span style="font-size:.9rem;">💎</span>
              <p style="font-family:'Outfit',sans-serif;font-size:.78rem;color:#7C7A9A;margin:0;">
                Pay <strong style="color:#A78BFA;">₹10</strong> to download full-resolution PNG &amp; JPG,
                no watermarks, re-download anytime.
              </p>
            </div>
            """, unsafe_allow_html=True)