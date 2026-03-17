import streamlit as st

def back_button(label="Back", destination="dashboard"):
    col, _ = st.columns([1, 7])
    with col:
        if st.button(label, key=f"back_{destination}_{label}", use_container_width=True):
            st.session_state["page"] = destination
            st.rerun()

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Syne+Mono&family=Outfit:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg:       #08080E;
  --bg2:      #0F0F18;
  --bg3:      #171723;
  --bg4:      #1E1E2E;
  --border:   rgba(255,255,255,0.06);
  --border2:  rgba(255,255,255,0.10);
  --text:     #EEEAF8;
  --text-m:   #7C7A9A;
  --text-dim: #3E3C58;
  --v:        #A78BFA;
  --v2:       #7C3AED;
  --pink:     #F472B6;
  --green:    #34D399;
  --blue:     #60A5FA;
  --gold:     #FBBF24;
  --grad:     linear-gradient(135deg,#A78BFA 0%,#F472B6 100%);
  --r:        12px;
  --r-lg:     18px;
}

@keyframes fade-up {
  from { opacity:0; transform:translateY(20px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes shimmer {
  0%   { background-position:-200% center; }
  100% { background-position: 200% center; }
}
@keyframes glow {
  0%,100% { box-shadow:0 0 20px rgba(167,139,250,.10); }
  50%     { box-shadow:0 0 40px rgba(167,139,250,.25); }
}
@keyframes border-pulse {
  0%,100% { border-color:rgba(167,139,250,.15); }
  50%     { border-color:rgba(167,139,250,.4); }
}

*,*::before,*::after{box-sizing:border-box;}

html,body,.stApp{
  background:var(--bg) !important;
  font-family:'Outfit',sans-serif !important;
  color:var(--text) !important;
}

.block-container{
  padding-top:1.5rem !important;
  padding-bottom:4rem !important;
  max-width:1240px !important;
  position:relative;z-index:1;
  animation:fade-up .4s cubic-bezier(.16,1,.3,1);
}

/* SIDEBAR */
[data-testid="stSidebar"]{
  background:var(--bg2) !important;
  border-right:1px solid var(--border) !important;
}
[data-testid="stSidebar"]>div{padding-top:0 !important;}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label{
  color:var(--text-m) !important;
  font-family:'Outfit',sans-serif !important;
}
[data-testid="stSidebar"] .stButton>button{
  background:transparent !important;
  color:var(--text-m) !important;
  border:1px solid transparent !important;
  border-radius:10px !important;
  padding:10px 14px !important;
  width:100% !important;text-align:left !important;
  font-size:.875rem !important;font-weight:500 !important;
  font-family:'Outfit',sans-serif !important;
  transition:all .15s ease !important;
  margin:2px 0 !important;box-shadow:none !important;
}
[data-testid="stSidebar"] .stButton>button:hover{
  background:var(--bg3) !important;
  color:var(--text) !important;
  border-color:var(--border) !important;
}

/* PRIMARY BTN */
.stButton>button[kind="primary"],
.stDownloadButton>button[kind="primary"]{
  background:var(--grad) !important;
  color:#fff !important;border:none !important;
  border-radius:10px !important;padding:13px 28px !important;
  font-weight:700 !important;font-size:.9rem !important;
  font-family:'Outfit',sans-serif !important;letter-spacing:.01em !important;
  box-shadow:0 4px 20px rgba(167,139,250,.25) !important;
  transition:all .2s cubic-bezier(.16,1,.3,1) !important;
}
.stButton>button[kind="primary"]:hover,
.stDownloadButton>button[kind="primary"]:hover{
  transform:translateY(-2px) !important;
  box-shadow:0 8px 32px rgba(167,139,250,.40) !important;
}

/* DEFAULT BTN */
.stButton>button:not([kind]),
.stDownloadButton>button:not([kind]){
  background:var(--bg3) !important;
  color:var(--text-m) !important;
  border:1px solid var(--border) !important;
  border-radius:10px !important;
  font-family:'Outfit',sans-serif !important;
  font-size:.875rem !important;font-weight:500 !important;
  transition:all .15s ease !important;box-shadow:none !important;
}
.stButton>button:not([kind]):hover,
.stDownloadButton>button:not([kind]):hover{
  background:var(--bg4) !important;
  border-color:var(--border2) !important;
  color:var(--text) !important;
  transform:translateY(-1px) !important;
}

/* INPUTS */
.stTextInput>div>div>input{
  background:var(--bg3) !important;
  border:1px solid var(--border) !important;
  border-radius:10px !important;color:var(--text) !important;
  padding:13px 16px !important;font-size:.9rem !important;
  font-family:'Outfit',sans-serif !important;
  transition:all .2s ease !important;
}
.stTextInput>div>div>input:focus{
  border-color:rgba(167,139,250,.5) !important;
  box-shadow:0 0 0 3px rgba(167,139,250,.1),0 0 20px rgba(167,139,250,.06) !important;
  background:var(--bg2) !important;outline:none !important;
}
.stTextInput>div>div>input::placeholder{color:var(--text-dim) !important;}
.stTextInput label{
  font-family:'Syne Mono',monospace !important;
  font-size:.6rem !important;text-transform:uppercase !important;
  letter-spacing:.1em !important;color:var(--text-dim) !important;
}

/* CHECKBOX */
.stCheckbox label span{
  color:var(--text-m) !important;
  font-family:'Outfit',sans-serif !important;font-size:.875rem !important;
}

/* SLIDER */
.stSlider label{
  font-family:'Syne Mono',monospace !important;font-size:.6rem !important;
  text-transform:uppercase !important;letter-spacing:.1em !important;color:var(--text-dim) !important;
}
.stSlider>div>div>div{background:var(--bg4) !important;}
.stSlider>div>div>div>div{background:var(--grad) !important;}

/* FILE UPLOADER */
[data-testid="stFileUploader"]{
  background:var(--bg3) !important;
  border:1.5px dashed rgba(167,139,250,.2) !important;
  border-radius:var(--r-lg) !important;
  transition:all .2s ease !important;
  animation:border-pulse 3s ease infinite !important;
}
[data-testid="stFileUploader"]:hover{
  border-color:rgba(167,139,250,.55) !important;
  background:rgba(167,139,250,.03) !important;
}
[data-testid="stFileUploader"] label{
  color:var(--text-m) !important;
  font-family:'Outfit',sans-serif !important;font-weight:600 !important;
}

/* METRICS */
[data-testid="metric-container"]{
  background:var(--bg2) !important;
  border:1px solid var(--border) !important;
  border-radius:var(--r) !important;padding:20px !important;
  transition:all .2s ease !important;
}
[data-testid="metric-container"]:hover{
  border-color:rgba(167,139,250,.25) !important;
  transform:translateY(-2px) !important;
  box-shadow:0 8px 30px rgba(0,0,0,.4) !important;
}
[data-testid="stMetricValue"]{
  color:var(--text) !important;font-family:'Syne',sans-serif !important;
  font-size:1.6rem !important;font-weight:700 !important;
}
[data-testid="stMetricLabel"]{
  color:var(--text-dim) !important;font-family:'Syne Mono',monospace !important;
  font-size:.57rem !important;text-transform:uppercase !important;letter-spacing:.12em !important;
}

/* ALERTS */
.stSuccess{background:rgba(52,211,153,.06) !important;border:1px solid rgba(52,211,153,.2) !important;border-radius:var(--r) !important;}
.stError{background:rgba(244,114,182,.06) !important;border:1px solid rgba(244,114,182,.2) !important;border-radius:var(--r) !important;}
.stWarning{background:rgba(251,191,36,.06) !important;border:1px solid rgba(251,191,36,.2) !important;border-radius:var(--r) !important;}
[data-testid="stAlert"]{
  font-family:'Outfit',sans-serif !important;
  border-left-width:0 !important;font-size:.9rem !important;color:var(--text) !important;
}

.stSpinner>div{border-top-color:var(--v) !important;}

[data-testid="stProgressBar"]{
  background:var(--bg3) !important;border-radius:99px !important;overflow:hidden !important;height:4px !important;
}
[data-testid="stProgressBar"]>div>div{
  background:linear-gradient(90deg,var(--v),var(--pink),var(--v)) !important;
  background-size:200% 100% !important;
  animation:shimmer 1.5s linear infinite !important;border-radius:99px !important;
}

[data-testid="stImage"] img{
  border-radius:var(--r) !important;
  box-shadow:0 8px 40px rgba(0,0,0,.6) !important;
}
.stImage p{
  font-family:'Syne Mono',monospace !important;font-size:.6rem !important;
  color:var(--text-dim) !important;text-transform:uppercase !important;
  letter-spacing:.1em !important;text-align:center !important;margin-top:8px !important;
}

::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--bg4);border-radius:99px;}
::-webkit-scrollbar-thumb:hover{background:var(--text-dim);}

#MainMenu,footer{display:none !important;}
header[data-testid="stHeader"]{display:none !important;}
[data-testid="stToolbar"]{display:none !important;}
[data-testid="stDecoration"]{display:none !important;}

hr{border-color:var(--border) !important;}
[data-testid="column"]{padding:0 5px !important;}
.stMarkdown p{font-family:'Outfit',sans-serif !important;color:var(--text-m) !important;}

.stSelectbox>div>div{
  background:var(--bg3) !important;border:1px solid var(--border) !important;
  border-radius:10px !important;color:var(--text) !important;font-family:'Outfit',sans-serif !important;
}
</style>
"""