# 🎨 Toonify — AI Art Studio

> Transform any photo into stunning artwork using 10 AI-powered effects. Built with Python, Streamlit, OpenCV, and Razorpay.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?style=flat-square&logo=streamlit)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?style=flat-square&logo=opencv)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

---

## ✨ Features

- **10 AI Art Effects** — Classic Cartoon, Watercolor, Neon Glow, Pencil Sketch, Oil Painting, Pixel Art, Vintage, Anime, Comic Book, Color Pencil
- **3 Intensity Levels** — Light, Medium, Strong for every effect
- **Before / After Comparison** — Side-by-side preview of original vs processed
- **User Authentication** — Register, login, password hashing with bcrypt
- **Image History & Gallery** — Browse all past artworks with filter and sort
- **Razorpay Payment Integration** — ₹10 per full-resolution download
- **Free Preview** — Watermarked comparison image available for free
- **Profile Dashboard** — Stats, payment history, password change
- **Download Formats** — PNG, JPG, comparison image, ZIP of all paid artworks
- **SQLite Database** — Zero-config local database

---

## 🖼️ App Pages

| Page | Description |
|------|-------------|
| Login | Sign in with username or email |
| Register | Create account with real-time password strength meter |
| Dashboard | Overview of artworks, stats, quick navigation |
| Art Studio | Upload image → choose effect → apply → download |
| Payment | Razorpay checkout for full-resolution download |
| Gallery | Browse, filter, sort and re-download all artworks |
| Profile | Account details, payment history, change password |

---

## 🗂️ Project Structure

```
toonify/
│
├── app.py                      # Main Streamlit entry point
│
├── frontend/
│   ├── login_page.py           # Login UI
│   ├── register_page.py        # Registration UI
│   ├── dashboard_page.py       # Dashboard UI
│   ├── image_processing_page.py# Art Studio UI
│   ├── payment_page.py         # Checkout, success, failure, history UI
│   └── other_pages.py          # Gallery + Profile UI
│
├── backend/
│   ├── auth.py                 # Login, register, password hashing, image history
│   ├── image_processor.py      # 10 OpenCV/Pillow art effects
│   └── download_manager.py     # File saving, watermarking, download prep
│
├── payment/
│   └── razorpay_handler.py     # Razorpay order creation & verification
│
├── database/
│   └── db.py                   # SQLite connection + schema init
│
├── utils/
│   └── styles.py               # Shared UI helpers (back button etc.)
│
├── uploads/                    # User uploaded originals (git-ignored)
├── processed/                  # AI processed outputs (git-ignored)
├── downloads/                  # Temp download files (git-ignored)
├── toonify.db               # SQLite database (git-ignored)
└── requirements.txt
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Prathmeshkangane/Toonify.git
cd Toonify
```

### 2. Create and activate virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root (never commit this):

```env
RAZORPAY_KEY_ID=rzp_test_your_key_id_here
RAZORPAY_KEY_SECRET=your_secret_here
```

### 5. Run the app

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 📦 Requirements

```
streamlit
opencv-python
Pillow
bcrypt
razorpay
python-dotenv
numpy
```

Install all at once:

```bash
pip install streamlit opencv-python Pillow bcrypt razorpay python-dotenv numpy
```

---

## 🎨 AI Effects

| # | Effect | Description |
|---|--------|-------------|
| 1 | 🎨 Classic Cartoon | Bold outlines with flat, vibrant colors |
| 2 | 🌊 Watercolor | Soft flowing watercolor painting |
| 3 | ⚡ Neon Glow | Cyberpunk neon edges on dark background |
| 4 | ✏️ Pencil Sketch | Realistic hand-drawn pencil sketch |
| 5 | 🖌️ Oil Painting | Rich textured oil-on-canvas look |
| 6 | 🕹️ Pixel Art | Retro 8-bit pixelated game art |
| 7 | 📷 Vintage | Warm film grain with vignette |
| 8 | 🌸 Anime | Smooth shading, sharp outlines |
| 9 | 💥 Comic Book | High-contrast posterized comic style |
| 10 | 🖍️ Color Pencil | Vivid colored pencil drawing |

All effects are processed locally using **OpenCV** and **Pillow** — no external AI API calls.

---

## 💳 Payment Flow

1. User processes an image in Art Studio
2. Clicks **Download · ₹10**
3. Razorpay checkout opens (test mode supported)
4. On success → full-resolution PNG + JPG unlocked
5. Re-download available anytime from Gallery

> **Demo mode** — click "Simulate Successful Payment" to test the full flow without real money.

---

## 🗄️ Database Schema

**users**
```
user_id | username | email | password (bcrypt) | created_at | last_login
```

**image_history**
```
id | user_id | original_image_path | processed_image_path | watermarked_path |
style_applied | download_format | file_size_kb | payment_status | processing_date
```

**Transactions**
```
id | user_id | razorpay_order_id | razorpay_payment_id | razorpay_signature |
amount | currency | status | image_ref | receipt | download_count | created_at | paid_at
```

---

## 🔐 Security

- Passwords hashed with **bcrypt**
- `.env` file for all secrets — never committed
- Razorpay signature verification on every payment
- GitHub Push Protection enabled on this repo

---

## 🚀 Deployment

The app can be deployed on **Streamlit Community Cloud**:

1. Push your code to GitHub (without `.env`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → set `app.py` as entry point
4. Add secrets under **Settings → Secrets**:
   ```toml
   RAZORPAY_KEY_ID = "rzp_test_..."
   RAZORPAY_KEY_SECRET = "your_secret"
   ```

---

## 👨‍💻 Built With

- [Streamlit](https://streamlit.io) — Web UI framework
- [OpenCV](https://opencv.org) — Computer vision effects
- [Pillow](https://python-pillow.org) — Image processing
- [bcrypt](https://github.com/pyca/bcrypt) — Password hashing
- [Razorpay](https://razorpay.com) — Payment gateway
- [SQLite](https://sqlite.org) — Local database

---

## 📄 License

MIT License — feel free to use, modify and distribute.

---

<p align="center">Made with ❤️ by Prathmesh Kangane</p>
