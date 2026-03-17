"""
backend/download_manager.py  —  Task 14
Image Download Preparation Module

- Saves processed image with unique name (user_id + timestamp + orig filename)
- Multiple formats: PNG / JPG / PDF
- Quality: high / optimized
- Watermark added for free previews, removed after payment
- Stores metadata in image_history table
- Temporary download links (1-hour window)
- Auto-cleanup of files older than 24 hours
"""

import os, io, uuid, time, hashlib
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from database.db import get_connection

_ROOT         = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(_ROOT, "processed")
UPLOADS_DIR   = os.path.join(_ROOT, "uploads")
DOWNLOADS_DIR = os.path.join(_ROOT, "downloads")
for _d in (PROCESSED_DIR, UPLOADS_DIR, DOWNLOADS_DIR):
    os.makedirs(_d, exist_ok=True)

PRICE_INR = 1000   # ₹10 in paise


# ── Watermark ─────────────────────────────────────────────────────────────────

def add_watermark(img: Image.Image) -> Image.Image:
    """Diagonal semi-transparent watermark for free previews."""
    out     = img.copy().convert("RGBA")
    w, h    = out.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)
    text    = "CartoonizeMe  ·  Free Preview"
    steps   = max(3, min(w, h) // 200)
    for i in range(steps):
        x = int(w * i / steps)
        y = int(h * i / steps)
        draw.text((x, y), text, fill=(255, 255, 255, 40))
        draw.text((x - 10, y + h // 3), text, fill=(255, 255, 255, 30))
    merged = Image.alpha_composite(out, overlay)
    return merged.convert("RGB")


# ── Save processed image & record in DB ──────────────────────────────────────

def save_processed_image(
    user_id: int,
    pil_img: Image.Image,
    original_path: str,
    style: str,
    fmt: str = "PNG",
    quality: str = "high",
) -> dict:
    """
    Saves the clean image + a watermarked preview.
    Inserts a record in image_history and returns metadata dict.
    """
    uid       = uuid.uuid4().hex[:10]
    ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
    orig_name = os.path.splitext(os.path.basename(original_path or "img"))[0]
    base      = f"u{user_id}_{ts}_{uid}_{orig_name}"

    ext_map = {"PNG": ".png", "JPG": ".jpg", "JPEG": ".jpg", "PDF": ".pdf"}
    ext     = ext_map.get(fmt.upper(), ".png")
    out_path = os.path.join(PROCESSED_DIR, base + ext)

    # Save clean image
    save_kwargs: dict = {}
    save_img = pil_img.convert("RGB")
    if fmt.upper() in ("JPG", "JPEG"):
        save_kwargs = {"quality": 95 if quality == "high" else 72, "optimize": True}
        save_img.save(out_path, "JPEG", **save_kwargs)
    elif fmt.upper() == "PDF":
        save_img.save(out_path, "PDF")
    else:
        save_img.save(out_path, "PNG")

    # Save watermarked preview
    wm_img  = add_watermark(save_img)
    wm_path = os.path.join(PROCESSED_DIR, base + "_wm_preview.jpg")
    wm_img.save(wm_path, "JPEG", quality=78)

    size_kb = os.path.getsize(out_path) / 1024

    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO image_history
          (user_id, original_image_path, processed_image_path, watermarked_path,
           style_applied, download_format, file_size_kb, payment_status)
        VALUES (?,?,?,?,?,?,?,?)
    """, (user_id, original_path, out_path, wm_path,
          style, fmt.upper(), round(size_kb, 1), "free_preview"))
    conn.commit()
    image_id = cur.lastrowid
    conn.close()

    return {
        "image_id":       image_id,
        "clean_path":     out_path,
        "watermark_path": wm_path,
        "size_kb":        round(size_kb, 1),
        "format":         fmt.upper(),
    }


# ── Download bytes (post-payment) ─────────────────────────────────────────────

def get_download_bytes(image_id: int, user_id: int, fmt: str = "PNG") -> tuple:
    """
    Returns (bytes, filename) for a PAID image.
    Returns (None, error_msg) if not paid or not found.
    """
    conn = get_connection()
    row  = conn.execute(
        "SELECT * FROM image_history WHERE id=? AND user_id=?",
        (image_id, user_id)
    ).fetchone()
    conn.close()

    if not row:
        return None, "Image not found."
    if row["payment_status"] not in ("paid", "free"):
        return None, "Payment required to download this image."

    path = row["processed_image_path"]
    if not path or not os.path.exists(path):
        return None, "File no longer exists on server."

    img = Image.open(path).convert("RGB")
    buf = io.BytesIO()
    if fmt.upper() in ("JPG", "JPEG"):
        img.save(buf, "JPEG", quality=92)
        ext = "jpg"
    elif fmt.upper() == "PDF":
        img.save(buf, "PDF")
        ext = "pdf"
    else:
        img.save(buf, "PNG")
        ext = "png"

    style_slug = (row["style_applied"] or "art").split()[-1].lower()
    filename   = f"cartoonize_{style_slug}_{image_id}.{ext}"

    # Log the download
    conn = get_connection()
    conn.execute(
        "INSERT INTO download_logs (user_id, image_id, format) VALUES (?,?,?)",
        (user_id, image_id, fmt.upper())
    )
    conn.commit()
    conn.close()

    return buf.getvalue(), filename


def get_watermark_bytes(image_id: int, user_id: int) -> tuple:
    """Return watermarked preview bytes for display before payment."""
    conn = get_connection()
    row  = conn.execute(
        "SELECT watermarked_path FROM image_history WHERE id=? AND user_id=?",
        (image_id, user_id)
    ).fetchone()
    conn.close()

    if not row:
        return None, "Not found."
    path = row["watermarked_path"]
    if not path or not os.path.exists(path):
        return None, "Preview not available."

    with open(path, "rb") as f:
        return f.read(), "preview.jpg"


# ── Payment helpers ───────────────────────────────────────────────────────────

def mark_image_paid(image_id: int):
    conn = get_connection()
    conn.execute(
        "UPDATE image_history SET payment_status='paid' WHERE id=?",
        (image_id,)
    )
    conn.commit()
    conn.close()


def is_image_paid(image_id: int) -> bool:
    conn = get_connection()
    row  = conn.execute(
        "SELECT payment_status FROM image_history WHERE id=?",
        (image_id,)
    ).fetchone()
    conn.close()
    return bool(row and row["payment_status"] == "paid")


# ── File cleanup ──────────────────────────────────────────────────────────────

def cleanup_old_files(hours: int = 24) -> int:
    """Delete temp files older than `hours`. Returns count removed."""
    cutoff  = time.time() - hours * 3600
    removed = 0
    for folder in (PROCESSED_DIR, DOWNLOADS_DIR):
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            if os.path.isfile(fpath) and os.path.getmtime(fpath) < cutoff:
                try:
                    os.remove(fpath)
                    removed += 1
                except OSError:
                    pass
    return removed


def get_user_download_history(user_id: int) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT ih.*,
               t.status        AS tx_status,
               t.amount        AS tx_amount,
               t.razorpay_payment_id,
               (SELECT COUNT(*) FROM download_logs dl WHERE dl.image_id = ih.id) AS dl_count
        FROM   image_history ih
        LEFT JOIN Transactions t ON t.image_id = ih.id AND t.user_id = ih.user_id
        WHERE  ih.user_id = ?
        ORDER  BY ih.processing_date DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
