"""
backend/image_processor.py
10 cartoon/art effects using OpenCV + Pillow only — no cloud API needed.

Each effect function signature:  fn(img: PIL.Image, intensity: str) -> (PIL.Image, float)
where intensity is "light" | "medium" | "strong"
and the float is elapsed seconds.

EFFECTS dict is what image_processing_page.py imports.
"""

import os
import time
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw
import cv2

ROOT = os.path.dirname(os.path.dirname(__file__))
PROCESSED_DIR = os.path.join(ROOT, "processed")
UPLOADS_DIR   = os.path.join(ROOT, "uploads")
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR,   exist_ok=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _pil_to_cv(img: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)

def _cv_to_pil(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))

def _intensity_map(intensity: str, low, mid, high):
    return {"light": low, "medium": mid, "strong": high}.get(intensity, mid)


# ── Effect 1: Classic Cartoon ─────────────────────────────────────────────────

def _cartoon(img: Image.Image, intensity: str):
    t0 = time.time()
    cv_img = _pil_to_cv(img)
    passes = _intensity_map(intensity, 1, 2, 3)
    color = cv_img.copy()
    for _ in range(passes):
        color = cv2.bilateralFilter(color, 9, 250, 250)
    gray  = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    gray  = cv2.medianBlur(gray, 7)
    block = _intensity_map(intensity, 7, 9, 11)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, block, 7)
    edges3 = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    result = cv2.bitwise_and(color, edges3)
    return _cv_to_pil(result), round(time.time() - t0, 2)


# ── Effect 2: Watercolor ──────────────────────────────────────────────────────

def _watercolor(img: Image.Image, intensity: str):
    t0 = time.time()
    cv_img = _pil_to_cv(img)
    sigma_s = _intensity_map(intensity, 40, 60, 80)
    sigma_r = _intensity_map(intensity, 0.35, 0.45, 0.55)
    result  = cv2.stylization(cv_img, sigma_s=sigma_s, sigma_r=sigma_r)
    pil = _cv_to_pil(result)
    pil = ImageEnhance.Color(pil).enhance(_intensity_map(intensity, 1.1, 1.4, 1.7))
    pil = pil.filter(ImageFilter.SMOOTH_MORE)
    return pil, round(time.time() - t0, 2)


# ── Effect 3: Neon Glow ───────────────────────────────────────────────────────

def _neon_glow(img: Image.Image, intensity: str):
    t0 = time.time()
    pil = img.convert("RGB")
    edges = pil.filter(ImageFilter.FIND_EDGES)
    bright = _intensity_map(intensity, 3.0, 5.0, 7.0)
    edges  = ImageEnhance.Brightness(edges).enhance(bright)
    edges  = ImageEnhance.Color(edges).enhance(6.0)
    dark_f = _intensity_map(intensity, 0.4, 0.25, 0.15)
    dark   = ImageEnhance.Brightness(pil).enhance(dark_f)
    blend  = _intensity_map(intensity, 0.6, 0.78, 0.9)
    result = Image.blend(dark, edges, blend)
    result = ImageEnhance.Color(result).enhance(3.5)
    return result, round(time.time() - t0, 2)


# ── Effect 4: Pencil Sketch ───────────────────────────────────────────────────

def _sketch(img: Image.Image, intensity: str):
    t0 = time.time()
    cv_img = _pil_to_cv(img)
    shade  = _intensity_map(intensity, 0.03, 0.05, 0.08)
    _, color_sketch = cv2.pencilSketch(cv_img, sigma_s=60, sigma_r=0.07, shade_factor=shade)
    gray_arr, _ = cv2.pencilSketch(cv_img, sigma_s=60, sigma_r=0.07, shade_factor=shade)
    # Blend grayscale + color for realism
    gray3 = cv2.cvtColor(gray_arr, cv2.COLOR_GRAY2BGR)
    blend_w = _intensity_map(intensity, 0.2, 0.5, 0.8)
    blended = cv2.addWeighted(gray3, 1 - blend_w, color_sketch, blend_w, 0)
    return _cv_to_pil(blended), round(time.time() - t0, 2)


# ── Effect 5: Oil Painting ────────────────────────────────────────────────────

def _oil_painting(img: Image.Image, intensity: str):
    t0 = time.time()
    cv_img = _pil_to_cv(img)
    # Simulate oil paint with bilateral + detail enhance
    passes = _intensity_map(intensity, 1, 2, 3)
    result = cv_img.copy()
    for _ in range(passes):
        result = cv2.bilateralFilter(result, 11, 100, 100)
    result = cv2.detailEnhance(result, sigma_s=12, sigma_r=0.18)
    pil = _cv_to_pil(result)
    pil = ImageEnhance.Color(pil).enhance(_intensity_map(intensity, 1.3, 1.6, 1.9))
    pil = ImageEnhance.Contrast(pil).enhance(_intensity_map(intensity, 1.1, 1.25, 1.4))
    return pil, round(time.time() - t0, 2)


# ── Effect 6: Pixel Art ───────────────────────────────────────────────────────

def _pixel_art(img: Image.Image, intensity: str):
    t0 = time.time()
    factor = _intensity_map(intensity, 10, 14, 20)
    w, h   = img.size
    small  = img.resize((w // factor, h // factor), Image.NEAREST)
    result = small.resize((w, h), Image.NEAREST)
    result = ImageEnhance.Color(result).enhance(1.4)
    result = ImageEnhance.Contrast(result).enhance(1.2)
    return result, round(time.time() - t0, 2)


# ── Effect 7: Vintage ─────────────────────────────────────────────────────────

def _vintage(img: Image.Image, intensity: str):
    t0 = time.time()
    pil = img.convert("RGB")
    # Desaturate slightly
    desat = _intensity_map(intensity, 0.6, 0.45, 0.3)
    pil   = ImageEnhance.Color(pil).enhance(desat)
    # Warm tone overlay
    r, g, b = pil.split()
    r = r.point(lambda x: min(x + _intensity_map(intensity, 20, 35, 50), 255))
    b = b.point(lambda x: max(x - _intensity_map(intensity, 15, 25, 38), 0))
    pil = Image.merge("RGB", (r, g, b))
    # Add grain
    arr   = np.array(pil, dtype=np.float32)
    noise = np.random.normal(0, _intensity_map(intensity, 8, 14, 22), arr.shape)
    arr   = np.clip(arr + noise, 0, 255).astype(np.uint8)
    pil   = Image.fromarray(arr)
    # Slight vignette
    w, h  = pil.size
    mask  = Image.new("L", (w, h), 255)
    draw  = ImageDraw.Draw(mask)
    strength = _intensity_map(intensity, 60, 90, 120)
    for i in range(strength):
        alpha = int(255 * (1 - (i / strength) ** 0.5))
        draw.rectangle([i, i, w - i - 1, h - i - 1], outline=alpha)
    pil   = Image.composite(pil, ImageEnhance.Brightness(pil).enhance(0.3), mask)
    return pil, round(time.time() - t0, 2)


# ── Effect 8: Anime ───────────────────────────────────────────────────────────

def _anime(img: Image.Image, intensity: str):
    t0 = time.time()
    cv_img = _pil_to_cv(img)
    # Smooth colors
    passes = _intensity_map(intensity, 2, 3, 4)
    color  = cv_img.copy()
    for _ in range(passes):
        color = cv2.bilateralFilter(color, 7, 200, 200)
    # Strong clean edges
    gray  = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    gray  = cv2.GaussianBlur(gray, (5, 5), 0)
    block = _intensity_map(intensity, 7, 9, 11)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY, block, 3)
    edges3 = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    result = cv2.bitwise_and(color, edges3)
    # Boost saturation
    pil = _cv_to_pil(result)
    pil = ImageEnhance.Color(pil).enhance(_intensity_map(intensity, 1.4, 1.8, 2.2))
    return pil, round(time.time() - t0, 2)


# ── Effect 9: Comic Book ──────────────────────────────────────────────────────

def _comic(img: Image.Image, intensity: str):
    t0 = time.time()
    cv_img = _pil_to_cv(img)
    # Posterize colors
    k = _intensity_map(intensity, 6, 5, 4)
    Z = cv_img.reshape((-1, 3)).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(Z, k, None, criteria, 3, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    flat    = centers[labels.flatten()]
    color   = flat.reshape(cv_img.shape)
    # Bold edges
    gray  = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,
                      _intensity_map(intensity, 60, 40, 25),
                      _intensity_map(intensity, 150, 120, 90))
    edges_inv = cv2.bitwise_not(edges)
    edges3    = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)
    result    = cv2.bitwise_and(color, edges3)
    pil = _cv_to_pil(result)
    pil = ImageEnhance.Contrast(pil).enhance(1.3)
    return pil, round(time.time() - t0, 2)


# ── Effect 10: Color Pencil ───────────────────────────────────────────────────

def _color_pencil(img: Image.Image, intensity: str):
    t0 = time.time()
    cv_img = _pil_to_cv(img)
    shade  = _intensity_map(intensity, 0.04, 0.07, 0.11)
    _, color_sketch = cv2.pencilSketch(cv_img, sigma_s=55, sigma_r=0.065, shade_factor=shade)
    pil = _cv_to_pil(color_sketch)
    pil = ImageEnhance.Color(pil).enhance(_intensity_map(intensity, 1.5, 2.0, 2.5))
    pil = ImageEnhance.Contrast(pil).enhance(1.15)
    return pil, round(time.time() - t0, 2)


# ── Image stats (used by image_processing_page.py) ───────────────────────────

def get_image_stats(img: Image.Image) -> dict:
    arr  = np.array(img.convert("RGB"))
    gray = np.mean(arr, axis=2)
    return {
        "width":      img.width,
        "height":     img.height,
        "brightness": round(float(np.mean(gray)), 1),
        "contrast":   round(float(np.std(gray)), 1),
    }


# ── Comparison image (used by image_processing_page.py) ──────────────────────

def create_comparison(original: Image.Image, processed: Image.Image, label: str = "") -> Image.Image:
    """Side-by-side before/after comparison image."""
    w = max(original.width, processed.width)
    h = max(original.height, processed.height)

    orig_r = original.resize((w, h), Image.LANCZOS)
    proc_r = processed.resize((w, h), Image.LANCZOS)

    gap    = 6
    out    = Image.new("RGB", (w * 2 + gap, h), (20, 20, 30))
    out.paste(orig_r, (0, 0))
    out.paste(proc_r, (w + gap, 0))

    draw = ImageDraw.Draw(out)
    # Simple text labels
    draw.rectangle([0, h - 22, w, h], fill=(10, 10, 18, 180))
    draw.rectangle([w + gap, h - 22, w * 2 + gap, h], fill=(10, 10, 18, 180))
    draw.text((8, h - 17), "ORIGINAL", fill=(120, 120, 150))
    short = label.split(" ", 1)[-1] if " " in label else label
    draw.text((w + gap + 8, h - 17), short.upper(), fill=(167, 139, 250))

    return out


# ── EFFECTS registry ──────────────────────────────────────────────────────────
# Keys match what image_processing_page.py displays and stores.

EFFECTS = {
    "🎨 Classic Cartoon": {
        "fn":   _cartoon,
        "icon": "🎨",
        "desc": "Bold outlines with flat, vibrant colors — classic cartoon look.",
    },
    "🌊 Watercolor":      {
        "fn":   _watercolor,
        "icon": "🌊",
        "desc": "Soft, flowing watercolor painting with organic color bleed.",
    },
    "⚡ Neon Glow":       {
        "fn":   _neon_glow,
        "icon": "⚡",
        "desc": "Cyberpunk neon edges glowing against a dark background.",
    },
    "✏️ Pencil Sketch":  {
        "fn":   _sketch,
        "icon": "✏️",
        "desc": "Realistic hand-drawn pencil sketch with subtle shading.",
    },
    "🖌️ Oil Painting":   {
        "fn":   _oil_painting,
        "icon": "🖌️",
        "desc": "Rich, textured oil-on-canvas aesthetic with deep colors.",
    },
    "🕹️ Pixel Art":      {
        "fn":   _pixel_art,
        "icon": "🕹️",
        "desc": "Retro 8-bit pixelated game art with punchy colors.",
    },
    "📷 Vintage":         {
        "fn":   _vintage,
        "icon": "📷",
        "desc": "Warm film grain, faded tones, and classic vignette.",
    },
    "🌸 Anime":           {
        "fn":   _anime,
        "icon": "🌸",
        "desc": "Smooth shading and sharp outlines inspired by Japanese animation.",
    },
    "💥 Comic Book":      {
        "fn":   _comic,
        "icon": "💥",
        "desc": "High-contrast posterized colors with bold comic-book edges.",
    },
    "🖍️ Color Pencil":   {
        "fn":   _color_pencil,
        "icon": "🖍️",
        "desc": "Vivid colored pencil drawing with visible strokes.",
    },
}