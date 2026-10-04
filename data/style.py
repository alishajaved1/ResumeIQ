import base64
import html
import io
import os

import streamlit as st

NAVY = "#0B1F4B"
BLUE = "#2563EB"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(180deg, #F4F7FC 0%, #EAF0FB 100%); }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.5rem; max-width: 1200px; }

/* ---------- animations ---------- */
@keyframes fadeUp { from {opacity:0; transform:translateY(18px);} to {opacity:1; transform:translateY(0);} }
@keyframes floaty { 0%,100% {transform:translateY(0);} 50% {transform:translateY(-10px);} }
@keyframes growBar { from {width:0;} }

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0B1F4B 0%, #14337A 100%); }
section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
.side-brand { font-size: 1.5rem; font-weight: 800; letter-spacing: .5px; margin-bottom: 2px; }
.side-sub { color: #BFD0F5 !important; font-size: .85rem; margin-bottom: 18px; }
.side-step { display:flex; gap:10px; align-items:flex-start; margin: 12px 0; padding: 10px 12px;
  background: rgba(255,255,255,.08); border-radius: 12px; transition: all .25s ease; }
.side-step:hover { background: rgba(255,255,255,.18); transform: translateX(4px); }
section[data-testid="stSidebar"] .side-num { background:#fff; color:#0B1F4B !important; font-weight:800; border-radius:50%;
  min-width:26px; height:26px; display:flex; align-items:center; justify-content:center; font-size:.8rem; }
.side-step span { font-size:.88rem; line-height:1.35; }

/* ---------- hero ---------- */
.hero { display:flex; align-items:center; justify-content:space-between; gap:24px;
  background: linear-gradient(135deg, #FFFFFF 0%, #E6EEFF 100%);
  border: 1px solid #D6E2FA; border-radius: 24px; padding: 28px 36px; margin-bottom: 22px;
  box-shadow: 0 10px 30px rgba(11,31,75,.10); animation: fadeUp .7s ease both; overflow:hidden; }
.hero-text { flex: 1.2; }
.hero-badge { display:inline-block; background:#0B1F4B; color:#fff; padding:5px 14px; border-radius:999px;
  font-size:.75rem; font-weight:600; letter-spacing:.8px; margin-bottom:12px; }
.hero h1 { font-size: 3rem; font-weight: 800; color:#0B1F4B; margin:0 0 8px 0; line-height:1.1; }
.hero h1 span { color:#2563EB; }
.hero p { color:#44557A; font-size:1.05rem; margin:0 0 16px 0; max-width: 520px; }
.chip { display:inline-block; background:#fff; color:#0B1F4B; border:1px solid #C9D8F7;
  padding:5px 12px; border-radius:999px; font-size:.8rem; font-weight:600; margin:0 6px 6px 0;
  transition: all .25s ease; }
.chip:hover { background:#0B1F4B; color:#fff; transform: translateY(-2px); }
.hero-img { flex: .8; display:flex; justify-content:center; }
.hero-img img { width: 100%; max-width: 330px; border-radius: 20px; mix-blend-mode: multiply;
  animation: floaty 5s ease-in-out infinite; }

/* ---------- KPI cards ---------- */
.kpi { background:#fff; border:1px solid #DCE6FA; border-left:6px solid #0B1F4B; border-radius:16px;
  padding:16px 20px; box-shadow:0 4px 14px rgba(11,31,75,.07); transition: all .3s ease;
  animation: fadeUp .6s ease both; }
.kpi:hover { transform: translateY(-6px); box-shadow:0 14px 28px rgba(11,31,75,.18); border-left-color:#2563EB; }
.kpi .ico { font-size:1.4rem; }
.kpi .lbl { color:#5B6B8F; font-size:.8rem; font-weight:600; text-transform:uppercase; letter-spacing:.6px; }
.kpi .val { color:#0B1F4B; font-size:1.9rem; font-weight:800; line-height:1.2; }

/* ---------- section titles / cards ---------- */
.sec { color:#0B1F4B; font-size:1.25rem; font-weight:700; margin: 22px 0 10px 0;
  padding-left:12px; border-left:5px solid #2563EB; }
.note { background:#EAF1FF; border:1px solid #C9D8F7; color:#0B1F4B; border-radius:14px;
  padding:14px 18px; margin:14px 0; animation: fadeUp .6s ease both; }

.cand { background:#fff; border:1px solid #DCE6FA; border-radius:18px; padding:16px 20px; margin-bottom:12px;
  box-shadow:0 4px 14px rgba(11,31,75,.06); transition: all .3s ease; animation: fadeUp .6s ease both; }
.cand:hover { transform: translateY(-4px) scale(1.005); box-shadow:0 14px 30px rgba(11,31,75,.16); border-color:#2563EB; }
.cand-top { display:flex; justify-content:space-between; align-items:center; gap:12px; }
.cand-title { color:#0B1F4B; font-weight:700; font-size:1.05rem; }
.cand-title small { color:#6B7BA0; font-weight:500; }
.pill { padding:4px 12px; border-radius:999px; font-size:.75rem; font-weight:700; }
.pill.Shortlist { background:#DCFCE7; color:#166534; }
.pill.Maybe { background:#FEF3C7; color:#92400E; }
.pill.Reject { background:#FEE2E2; color:#991B1B; }
.bar { background:#E3EBFA; height:10px; border-radius:99px; margin:12px 0 4px 0; overflow:hidden; }
.bar > div { height:100%; background: linear-gradient(90deg,#0B1F4B,#2563EB); border-radius:99px; animation: growBar 1.1s ease both; }
.score { color:#0B1F4B; font-weight:800; }
.tag { display:inline-block; background:#E6EEFF; color:#0B1F4B; border-radius:8px; padding:3px 9px; font-size:.75rem; margin:2px 4px 2px 0; }
.tag.miss { background:#FFF1F2; color:#9F1239; }
.reason { color:#44557A; font-size:.9rem; margin-top:6px; }

.result-card { background:#fff; border:1px solid #DCE6FA; border-radius:18px; padding:18px 22px; margin-bottom:12px;
  box-shadow:0 4px 14px rgba(11,31,75,.06); transition: all .3s ease; animation: fadeUp .6s ease both; }
.result-card:hover { transform: translateY(-4px); box-shadow:0 14px 30px rgba(11,31,75,.15); }
.result-card h4 { color:#0B1F4B; margin:0 0 8px 0; }
.result-card li, .result-card p { color:#33446B; font-size:.93rem; }

/* ---------- tabs ---------- */
.stTabs [role="tablist"] { gap: 8px; background:#fff; padding:6px; border-radius:14px;
  border:1px solid #DCE6FA; box-shadow:0 4px 12px rgba(11,31,75,.06); }
.stTabs [role="tab"] { border-radius:10px; padding:8px 18px; font-weight:600; color:#44557A;
  transition: all .25s ease; }
.stTabs [role="tab"]:hover { background:#EAF1FF; color:#0B1F4B; }
.stTabs [role="tab"][aria-selected="true"] { background:#0B1F4B; }
.stTabs [role="tab"][aria-selected="true"] p, .stTabs [role="tab"][aria-selected="true"] * { color:#fff !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"],
.stTabs .react-aria-SelectionIndicator { display:none !important; }
.stTabs [role="tabpanel"] { animation: fadeUp .5s ease both; padding-top: 12px; }

/* slider / progress ka rang navy */
div[data-testid="stSlider"] [role="slider"] { background:#0B1F4B !important; border-color:#0B1F4B !important; }
div[data-testid="stProgress"] > div > div > div { background:#2563EB !important; }

/* ---------- buttons ---------- */
.stButton > button, .stDownloadButton > button {
  background: linear-gradient(135deg, #0B1F4B, #1E3A8A); color:#fff; border:none; border-radius:12px;
  padding:.6rem 1.4rem; font-weight:600; transition: all .25s ease; box-shadow:0 4px 12px rgba(11,31,75,.25); }
.stButton > button:hover, .stDownloadButton > button:hover {
  background: linear-gradient(135deg, #2563EB, #1E3A8A); color:#fff; transform: translateY(-3px);
  box-shadow:0 10px 22px rgba(37,99,235,.35); }
.stButton > button:active { transform: translateY(0); }

/* ---------- inputs / tables ---------- */
.stTextArea textarea, .stTextInput input { border-radius:12px !important; border:1px solid #C9D8F7 !important; background:#fff; }
.stTextArea textarea:focus, .stTextInput input:focus { border-color:#2563EB !important; box-shadow:0 0 0 3px rgba(37,99,235,.18) !important; }
div[data-testid="stDataFrame"] { border:1px solid #DCE6FA; border-radius:14px; overflow:hidden;
  box-shadow:0 4px 14px rgba(11,31,75,.06); }
.stAlert { border-radius:14px; }
.footer { text-align:center; color:#6B7BA0; font-size:.8rem; margin:30px 0 8px 0; }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data
def _hero_b64(path="assets/hero.png"):
    """Image ko chhota kar ke base64 banata hai (page tez rahe)."""
    if not os.path.exists(path):
        return ""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.thumbnail((640, 640))
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode()


def hero():
    b64 = _hero_b64()
    img = f'<div class="hero-img"><img src="data:image/jpeg;base64,{b64}"/></div>' if b64 else ""
    st.markdown(
        '<div class="hero"><div class="hero-text">'
        '<div class="hero-badge">AI-POWERED HIRING</div>'
        '<h1>Resume<span>IQ</span></h1>'
        '<p>Resumes ko samajhne, score karne aur behtar banane ka smart tareeqa. '
        'Tez shortlist, explainable AI aur career coaching, sab ek jagah.</p>'
        '<span class="chip">⚡ TF-IDF Search</span><span class="chip">🤖 Gemini AI</span>'
        '<span class="chip">📊 Live Dashboard</span><span class="chip">⚖️ Fair Screening</span>'
        f'</div>{img}</div>', unsafe_allow_html=True)


def sidebar():
    with st.sidebar:
        st.markdown(
            '<div class="side-brand">📄 ResumeIQ</div>'
            '<div class="side-sub">Smart Resume Screening</div>'
            '<div class="side-step"><div class="side-num">1</div><span>Dashboard se data aur categories samjhein</span></div>'
            '<div class="side-step"><div class="side-num">2</div><span>Job Matcher mein job description likh kar best candidates payein</span></div>'
            '<div class="side-step"><div class="side-num">3</div><span>Resume Analyzer se apna resume behtar banayein</span></div>'
            '<div class="side-step"><div class="side-num">4</div><span>Ask AI se data par sawal poochein</span></div>',
            unsafe_allow_html=True)


def kpi(col, icon, label, value):
    col.markdown(
        f'<div class="kpi"><div class="ico">{icon}</div><div class="lbl">{html.escape(str(label))}</div>'
        f'<div class="val">{html.escape(str(value))}</div></div>', unsafe_allow_html=True)


def section(title):
    st.markdown(f'<div class="sec">{html.escape(title)}</div>', unsafe_allow_html=True)


def note(text):
    st.markdown(f'<div class="note">{html.escape(text)}</div>', unsafe_allow_html=True)


def _tags(csv_text, cls=""):
    items = [x.strip() for x in str(csv_text).split(",") if x.strip() and x.strip().lower() != "nan"]
    return "".join(f'<span class="tag {cls}">{html.escape(x)}</span>' for x in items[:8])


def candidate_card(rank, row):
    score = max(0, min(100, int(row["score"])))
    rec = str(row["recommendation"])
    rec_cls = rec if rec in ("Shortlist", "Maybe", "Reject") else "Maybe"
    st.markdown(
        f'<div class="cand"><div class="cand-top">'
        f'<div class="cand-title">#{rank} &nbsp; {html.escape(str(row["Category"]))} '
        f'<small>(Resume ID {int(row["resume_id"])})</small></div>'
        f'<div><span class="score">{score}/100</span> &nbsp; <span class="pill {rec_cls}">{html.escape(rec)}</span></div></div>'
        f'<div class="bar"><div style="width:{score}%"></div></div>'
        f'<div>✅ {_tags(row["matched_skills"])}</div>'
        f'<div>⚠️ {_tags(row["missing_skills"], "miss")}</div>'
        f'<div class="reason">{html.escape(str(row["reason"]))}</div></div>',
        unsafe_allow_html=True)


def result_card(title, items):
    if isinstance(items, str):
        items = [x.strip() for x in items.split("|") if x.strip()]
    lis = "".join(f"<li>{html.escape(str(i))}</li>" for i in items)
    st.markdown(f'<div class="result-card"><h4>{title}</h4><ul>{lis}</ul></div>', unsafe_allow_html=True)


def footer():
    st.markdown('<div class="footer">ResumeIQ • Built with Streamlit, scikit-learn & Gemini • Women Tech Quest 2026</div>',
                unsafe_allow_html=True)