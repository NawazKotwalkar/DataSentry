import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime
import io
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ingest import ingest
from src.quality_score import calculate_quality_score
from src.rules_engine import run_rules_engine

st.set_page_config(
    page_title="DataSentry",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ═══════════════════════════════════
   TOKENS
═══════════════════════════════════ */
:root {
    --ink:        #111827;
    --ink-2:      #374151;
    --ink-3:      #6B7280;
    --ink-4:      #9CA3AF;
    --line:       #E5E7EB;
    --surface:    #FFFFFF;
    --bg:         #F9FAFB;
    --bg-2:       #F3F4F6;
    --indigo:     #4F46E5;
    --indigo-l:   #EEF2FF;
    --indigo-m:   #C7D2FE;
    --violet:     #7C3AED;
    --emerald:    #059669;
    --emerald-l:  #ECFDF5;
    --emerald-m:  #6EE7B7;
    --amber:      #D97706;
    --amber-l:    #FFFBEB;
    --amber-m:    #FCD34D;
    --rose:       #E11D48;
    --rose-l:     #FFF1F2;
    --rose-m:     #FDA4AF;
    --r4:  4px;
    --r8:  8px;
    --r12: 12px;
    --r16: 16px;
    --r24: 24px;
    --s1: 0 1px 2px rgba(0,0,0,.06),0 1px 3px rgba(0,0,0,.1);
    --s2: 0 4px 6px -1px rgba(0,0,0,.07),0 2px 4px -1px rgba(0,0,0,.05);
    --s3: 0 10px 15px -3px rgba(0,0,0,.08),0 4px 6px -2px rgba(0,0,0,.04);
    --s4: 0 20px 25px -5px rgba(0,0,0,.1),0 10px 10px -5px rgba(0,0,0,.04);
}

/* ═══════════════════════════════════
   RESET
═══════════════════════════════════ */
*,*::before,*::after{box-sizing:border-box;}
html,body,[class*="css"],.stApp{
    font-family:'Plus Jakarta Sans',-apple-system,sans-serif !important;
    background:var(--bg) !important;
    color:var(--ink) !important;
    -webkit-font-smoothing:antialiased;
}
#MainMenu,footer,header,.stDeployButton,
[data-testid="stToolbar"]{visibility:hidden !important;display:none !important;}
[data-testid="stSidebar"],
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"]{display:none !important;}

/* ═══════════════════════════════════
   KEYFRAMES
═══════════════════════════════════ */
@keyframes fadeUp{
    from{opacity:0;transform:translateY(24px);}
    to{opacity:1;transform:translateY(0);}
}
@keyframes fadeIn{from{opacity:0;}to{opacity:1;}}
@keyframes slideDown{
    from{opacity:0;transform:translateY(-16px);}
    to{opacity:1;transform:translateY(0);}
}
@keyframes scaleUp{
    from{opacity:0;transform:scale(.94);}
    to{opacity:1;transform:scale(1);}
}
@keyframes shimmer{
    0%{background-position:-400px 0;}
    100%{background-position:400px 0;}
}
@keyframes glowPulse{
    0%,100%{box-shadow:0 0 0 0 rgba(79,70,229,.2);}
    50%{box-shadow:0 0 0 8px rgba(79,70,229,0);}
}
@keyframes borderFlow{
    0%{background-position:0% 50%;}
    50%{background-position:100% 50%;}
    100%{background-position:0% 50%;}
}
@keyframes float{
    0%,100%{transform:translateY(0);}
    50%{transform:translateY(-6px);}
}
@keyframes countIn{
    from{opacity:0;transform:scale(.8) translateY(8px);}
    to{opacity:1;transform:scale(1) translateY(0);}
}
@keyframes lineGrow{
    from{width:0;}to{width:100%;}
}

.au{animation:fadeUp .5s cubic-bezier(.22,.68,0,1.2) both;}
.ad{animation:slideDown .4s ease both;}
.as{animation:scaleUp .4s cubic-bezier(.22,.68,0,1.2) both;}
.af{animation:fadeIn .4s ease both;}
.d1{animation-delay:.05s;} .d2{animation-delay:.10s;}
.d3{animation-delay:.15s;} .d4{animation-delay:.20s;}
.d5{animation-delay:.25s;} .d6{animation-delay:.30s;}

/* ═══════════════════════════════════
   NAV BAR
═══════════════════════════════════ */
.navbar{
    display:flex;align-items:center;justify-content:space-between;
    padding:16px 24px;
    background:var(--surface);
    border-bottom:1px solid var(--line);
    box-shadow:var(--s1);
    margin-bottom:0;
    animation:slideDown .4s ease both;
    position:sticky;top:0;z-index:100;
}
.nav-brand{display:flex;align-items:center;gap:12px;}
.nav-icon{
    width:40px;height:40px;
    background:linear-gradient(135deg,var(--indigo),var(--violet));
    border-radius:var(--r12);
    display:flex;align-items:center;justify-content:center;
    font-size:1.2rem;
    box-shadow:var(--s2);
    animation:glowPulse 3s ease infinite;
}
.nav-title{
    font-size:1.15rem;font-weight:800;color:var(--ink);
    letter-spacing:-.025em;
}
.nav-sub{
    font-size:.65rem;font-weight:600;
    color:var(--ink-3);letter-spacing:.08em;
    text-transform:uppercase;margin-top:1px;
}
.nav-badge{
    font-size:.65rem;font-weight:700;
    background:var(--indigo-l);color:var(--indigo);
    border:1px solid var(--indigo-m);
    padding:3px 10px;border-radius:20px;
    letter-spacing:.04em;
}

/* ═══════════════════════════════════
   HERO SECTION
═══════════════════════════════════ */
.hero{
    text-align:center;
    padding:72px 24px 56px;
    background:linear-gradient(180deg,#FAFBFF 0%,var(--bg) 100%);
    border-bottom:1px solid var(--line);
    position:relative;overflow:hidden;
}
.hero::before{
    content:'';position:absolute;
    top:-60px;left:50%;transform:translateX(-50%);
    width:600px;height:600px;
    background:radial-gradient(circle,rgba(79,70,229,.08) 0%,transparent 70%);
    pointer-events:none;
}
.hero-eyebrow{
    display:inline-flex;align-items:center;gap:6px;
    background:var(--indigo-l);color:var(--indigo);
    border:1px solid var(--indigo-m);
    font-size:.72rem;font-weight:700;
    letter-spacing:.06em;text-transform:uppercase;
    padding:5px 14px;border-radius:20px;
    margin-bottom:20px;
    animation:scaleUp .5s ease both;
}
.hero h1{
    font-size:3.2rem !important;font-weight:800 !important;
    color:var(--ink) !important;
    letter-spacing:-.045em;line-height:1.1;
    margin-bottom:20px;
    animation:fadeUp .6s .05s ease both;
}
.hero h1 .grad{
    background:linear-gradient(135deg,var(--indigo) 0%,var(--violet) 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    background-clip:text;
}
.hero-sub{
    font-size:1.05rem !important;color:var(--ink-3) !important;
    line-height:1.7;max-width:560px;margin:0 auto 40px;
    animation:fadeUp .6s .1s ease both;
}
.hero-stats{
    display:flex;justify-content:center;gap:40px;flex-wrap:wrap;
    animation:fadeUp .6s .15s ease both;
}
.hero-stat-val{
    font-family:'JetBrains Mono',monospace;
    font-size:1.8rem;font-weight:600;
    color:var(--indigo);
}
.hero-stat-label{
    font-size:.72rem;font-weight:600;
    color:var(--ink-4);text-transform:uppercase;
    letter-spacing:.07em;margin-top:2px;
}

/* ═══════════════════════════════════
   FEATURE CARDS
═══════════════════════════════════ */
.features-section{
    padding:60px 0 48px;
    background:var(--bg);
}
.feature-card{
    background:var(--surface);
    border:1px solid var(--line);
    border-radius:var(--r16);
    padding:28px 22px;
    text-align:center;
    box-shadow:var(--s1);
    transition:all .3s cubic-bezier(.22,.68,0,1.2);
    cursor:default;
    position:relative;overflow:hidden;
}
.feature-card::before{
    content:'';position:absolute;
    inset:0;border-radius:var(--r16);
    background:linear-gradient(135deg,var(--indigo),var(--violet));
    opacity:0;transition:opacity .3s;
    z-index:0;
}
.feature-card:hover{
    transform:translateY(-6px);
    box-shadow:var(--s4);
    border-color:var(--indigo-m);
}
.feature-card:hover::before{opacity:.04;}
.feature-card>*{position:relative;z-index:1;}
.feature-icon-wrap{
    width:52px;height:52px;
    background:var(--indigo-l);
    border-radius:var(--r12);
    display:flex;align-items:center;justify-content:center;
    font-size:1.5rem;
    margin:0 auto 16px;
    transition:all .3s ease;
}
.feature-card:hover .feature-icon-wrap{
    background:linear-gradient(135deg,var(--indigo),var(--violet));
    box-shadow:0 8px 20px rgba(79,70,229,.3);
    transform:scale(1.1) rotate(-3deg);
}
.feature-title{
    font-weight:800;font-size:.95rem;
    color:var(--ink) !important;margin-bottom:8px;
}
.feature-desc{
    font-size:.8rem;color:var(--ink-3) !important;
    line-height:1.65;
}

/* ═══════════════════════════════════
   UPLOAD SECTION
═══════════════════════════════════ */
.upload-section{
    background:var(--surface);
    border:1px solid var(--line);
    border-radius:var(--r16);
    padding:32px;
    box-shadow:var(--s2);
    margin-bottom:8px;
    position:relative;overflow:hidden;
}
.upload-section::after{
    content:'';
    position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,var(--indigo),var(--violet),var(--indigo));
    background-size:200% 100%;
    animation:borderFlow 3s ease infinite;
}
.upload-title{
    font-weight:800;font-size:1rem;
    color:var(--ink);margin-bottom:4px;
}
.upload-sub{
    font-size:.78rem;color:var(--ink-3);margin-bottom:20px;
}

/* File uploader */
[data-testid="stFileUploader"]{
    background:var(--bg) !important;
    border:1.5px dashed var(--line) !important;
    border-radius:var(--r12) !important;
    transition:all .2s !important;
}
[data-testid="stFileUploader"]:hover{
    border-color:var(--indigo) !important;
    background:var(--indigo-l) !important;
}
[data-testid="stFileUploadDropzone"] p,
[data-testid="stFileUploadDropzone"] span,
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] small{
    color:var(--ink-3) !important;font-size:.78rem !important;
}
[data-testid="stFileUploader"] button{
    background:var(--surface) !important;
    border:1px solid var(--line) !important;
    color:var(--ink) !important;
    border-radius:var(--r8) !important;
    font-weight:700 !important;font-size:.75rem !important;
    padding:6px 14px !important;
    transition:all .2s !important;
}
[data-testid="stFileUploader"] button:hover{
    border-color:var(--indigo) !important;
    color:var(--indigo) !important;
}

/* ═══════════════════════════════════
   HISTORY ROWS
═══════════════════════════════════ */
.hist-row{
    display:flex;justify-content:space-between;align-items:center;
    padding:8px 12px;border-radius:var(--r8);margin-bottom:4px;
    background:var(--bg);border:1px solid var(--line);
    transition:all .2s;
}
.hist-row:hover{border-color:var(--indigo-m);background:var(--indigo-l);}
.hist-name{font-size:.75rem !important;color:var(--ink-2) !important;font-weight:600 !important;}
.hist-score{font-family:'JetBrains Mono',monospace !important;font-size:.75rem !important;font-weight:700 !important;}

/* ═══════════════════════════════════
   SECTION LABEL
═══════════════════════════════════ */
.sec-label{
    font-size:.62rem !important;font-weight:700 !important;
    letter-spacing:.1em;text-transform:uppercase;
    color:var(--ink-4) !important;
    margin-bottom:8px;display:block;
}

/* ═══════════════════════════════════
   PAGE HEADER
═══════════════════════════════════ */
.page-hdr{padding-bottom:16px;animation:fadeUp .4s ease both;}
.page-title{
    font-size:1.4rem !important;font-weight:800 !important;
    color:var(--ink) !important;letter-spacing:-.02em;
}
.page-meta{font-size:.78rem !important;color:var(--ink-3) !important;margin-top:3px;}

/* ═══════════════════════════════════
   BADGES
═══════════════════════════════════ */
.badge{
    display:inline-flex;align-items:center;gap:5px;
    font-size:.68rem !important;font-weight:700 !important;
    letter-spacing:.05em;text-transform:uppercase;
    padding:5px 12px;border-radius:20px;
}
.badge-healthy{background:var(--emerald-l);color:var(--emerald) !important;border:1px solid var(--emerald-m);}
.badge-warning{background:var(--amber-l);color:var(--amber) !important;border:1px solid var(--amber-m);}
.badge-critical{background:var(--rose-l);color:var(--rose) !important;border:1px solid var(--rose-m);}

/* ═══════════════════════════════════
   KPI CARDS
═══════════════════════════════════ */
.kpi{
    background:var(--surface);
    border:1px solid var(--line);
    border-radius:var(--r12);
    padding:18px 20px;min-height:96px;
    display:flex;flex-direction:column;justify-content:center;
    box-shadow:var(--s1);
    transition:all .25s ease;
    position:relative;overflow:hidden;
    animation:countIn .5s cubic-bezier(.22,.68,0,1.2) both;
}
.kpi::before{
    content:'';position:absolute;
    top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,var(--indigo),var(--violet));
    transform:scaleX(0);transform-origin:left;
    transition:transform .3s ease;
}
.kpi:hover{transform:translateY(-3px);box-shadow:var(--s3);}
.kpi:hover::before{transform:scaleX(1);}
.kpi-val{
    font-family:'JetBrains Mono',monospace !important;
    font-size:1.5rem !important;font-weight:600 !important;
    line-height:1.1;margin-bottom:5px;
}
.kpi-lbl{
    font-size:.62rem !important;font-weight:700 !important;
    letter-spacing:.09em;text-transform:uppercase;
    color:var(--ink-4) !important;
}

/* ═══════════════════════════════════
   SECTION TITLE
═══════════════════════════════════ */
.sec-title{
    font-size:.62rem !important;font-weight:700 !important;
    letter-spacing:.12em;text-transform:uppercase;
    color:var(--ink-4) !important;
    margin-bottom:12px;padding-bottom:10px;
    border-bottom:1px solid var(--line);
}

/* ═══════════════════════════════════
   TABS
═══════════════════════════════════ */
.stTabs [data-baseweb="tab-list"]{
    background:var(--surface) !important;
    border:1px solid var(--line) !important;
    border-radius:var(--r12) !important;
    padding:4px !important;gap:3px !important;
}
.stTabs [data-baseweb="tab"]{
    background:transparent !important;
    color:var(--ink-3) !important;
    border-radius:var(--r8) !important;
    font-size:.78rem !important;font-weight:600 !important;
    padding:7px 16px !important;
    transition:all .18s ease !important;border:none !important;
}
.stTabs [data-baseweb="tab"]:hover{
    background:var(--bg-2) !important;color:var(--ink) !important;
}
.stTabs [aria-selected="true"]{
    background:linear-gradient(135deg,var(--indigo),var(--violet)) !important;
    color:#fff !important;
    box-shadow:0 2px 8px rgba(79,70,229,.3) !important;
}
.stTabs [data-baseweb="tab-panel"]{padding-top:20px !important;}

/* ═══════════════════════════════════
   ISSUE CARDS
═══════════════════════════════════ */
.issue-card{
    background:var(--surface);
    border:1px solid var(--line);
    border-left:4px solid var(--line);
    border-radius:var(--r12);
    padding:16px 18px;margin-bottom:10px;
    box-shadow:var(--s1);
    transition:all .22s ease;
    animation:fadeUp .4s ease both;
}
.issue-card:hover{
    transform:translateX(4px);
    box-shadow:var(--s3);
    border-color:var(--line);
}
.issue-card.critical{border-left-color:var(--rose);}
.issue-card.high{border-left-color:var(--amber);}
.issue-card.medium{border-left-color:var(--indigo);}
.issue-rule{font-weight:700 !important;font-size:.9rem !important;color:var(--ink) !important;}
.issue-col{
    display:inline-block;font-size:.7rem !important;font-weight:600 !important;
    color:var(--ink-3) !important;background:var(--bg-2);
    padding:2px 8px;border-radius:var(--r4);margin-left:8px;
}
.issue-cost{
    font-family:'JetBrains Mono',monospace !important;
    font-weight:700 !important;color:var(--rose) !important;font-size:.95rem !important;
}
.issue-rec{font-size:.82rem !important;color:var(--ink-2) !important;margin-top:8px;line-height:1.55;}
.issue-meta{font-size:.68rem !important;color:var(--ink-4) !important;margin-top:5px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;}

/* ═══════════════════════════════════
   EXEC BOX
═══════════════════════════════════ */
.exec-box{
    background:var(--surface);
    border:1px solid var(--line);
    border-radius:var(--r12);
    padding:22px 24px;
    font-size:.92rem !important;line-height:1.75;
    color:var(--ink-2) !important;
    box-shadow:var(--s1);
}

/* ═══════════════════════════════════
   DROPDOWN FIX
═══════════════════════════════════ */
[data-baseweb="select"] *{color:var(--ink) !important;background:var(--surface) !important;}
[data-baseweb="popover"] *{color:var(--ink) !important;background:var(--surface) !important;}
[data-baseweb="menu"]{
    background:var(--surface) !important;
    border:1px solid var(--line) !important;
    border-radius:var(--r12) !important;
    box-shadow:var(--s3) !important;
}
[data-baseweb="menu"] li{color:var(--ink) !important;font-size:.85rem !important;}
[data-baseweb="menu"] li:hover{background:var(--indigo-l) !important;color:var(--indigo) !important;}

/* ═══════════════════════════════════
   METRICS
═══════════════════════════════════ */
[data-testid="stMetric"]{
    background:var(--surface) !important;
    border:1px solid var(--line) !important;
    border-radius:var(--r12) !important;
    padding:14px 16px !important;box-shadow:var(--s1) !important;
}
[data-testid="stMetricLabel"]>div,[data-testid="stMetricLabel"] p{
    color:var(--ink-3) !important;font-size:.7rem !important;
    font-weight:700 !important;text-transform:uppercase !important;
    letter-spacing:.07em !important;
}
[data-testid="stMetricValue"]>div,[data-testid="stMetricValue"] p{
    color:var(--ink) !important;
    font-family:'JetBrains Mono',monospace !important;
    font-size:1.25rem !important;font-weight:600 !important;
}

/* ═══════════════════════════════════
   DATAFRAME
═══════════════════════════════════ */
[data-testid="stDataFrame"]{
    border:1px solid var(--line) !important;
    border-radius:var(--r12) !important;
    overflow:hidden !important;box-shadow:var(--s1) !important;
}
[data-testid="stDataFrame"] *{color:var(--ink) !important;}

/* ═══════════════════════════════════
   EXPANDERS
═══════════════════════════════════ */
[data-testid="stExpander"]{
    background:var(--surface) !important;
    border:1px solid var(--line) !important;
    border-radius:var(--r12) !important;box-shadow:var(--s1) !important;
}
[data-testid="stExpander"] summary{color:var(--ink) !important;font-weight:600 !important;font-size:.85rem !important;}
[data-testid="stExpander"] *{color:var(--ink) !important;}

/* ═══════════════════════════════════
   DOWNLOAD BUTTON
═══════════════════════════════════ */
.stDownloadButton button{
    background:linear-gradient(135deg,var(--indigo),var(--violet)) !important;
    color:#fff !important;border:none !important;
    padding:9px 22px !important;border-radius:var(--r8) !important;
    font-weight:700 !important;font-size:.8rem !important;
    box-shadow:0 2px 8px rgba(79,70,229,.3) !important;
    transition:all .2s ease !important;cursor:pointer !important;
    letter-spacing:.02em !important;
}
.stDownloadButton button:hover{
    box-shadow:0 6px 16px rgba(79,70,229,.4) !important;
    transform:translateY(-1px) !important;
}

/* ═══════════════════════════════════
   ALERTS
═══════════════════════════════════ */
.stAlert{border-radius:var(--r12) !important;font-size:.85rem !important;}
[data-testid="stInfo"]{background:var(--indigo-l) !important;color:#3730A3 !important;border-color:var(--indigo-m) !important;}
[data-testid="stSuccess"]{background:var(--emerald-l) !important;color:#065F46 !important;border-color:var(--emerald-m) !important;}
.stAlert p{color:inherit !important;}
.stSpinner>div{border-top-color:var(--indigo) !important;}
hr{border:none !important;border-top:1px solid var(--line) !important;margin:24px 0 !important;}

/* ═══════════════════════════════════
   FOOTER
═══════════════════════════════════ */
.footer{
    text-align:center;padding:40px 20px 24px;
    border-top:1px solid var(--line);margin-top:48px;
}
.footer p{font-size:.72rem !important;color:var(--ink-4) !important;font-weight:600 !important;letter-spacing:.06em;text-transform:uppercase;}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ── Utilities ─────────────────────────────────────────────────────────────────
def sc(s): return "#059669" if s>=95 else "#D97706" if s>=80 else "#E11D48"

def badge(status):
    cls={"HEALTHY":"badge-healthy","WARNING":"badge-warning","CRITICAL":"badge-critical"}.get(status,"badge-warning")
    dot={"HEALTHY":"🟢","WARNING":"🟡","CRITICAL":"🔴"}.get(status,"🟡")
    return f'<span class="badge {cls}">{dot} {status}</span>'

def sty(ax,fig):
    ax.set_facecolor('#FFFFFF');fig.patch.set_facecolor('#FFFFFF')
    for s in['top','right']:ax.spines[s].set_visible(False)
    for s in['left','bottom']:ax.spines[s].set_color('#E5E7EB')
    ax.tick_params(colors='#6B7280',labelsize=8)

def run_analysis(fp,fn):
    df,ing=ingest(fp)
    qr=calculate_quality_score(df)
    br=run_rules_engine(df)
    st.session_state.history.append({"name":fn,"score":qr["overall_score"],"time":datetime.now().strftime("%H:%M")})
    return df,ing,qr,br

def summary(qr,br,fn):
    s=qr["overall_score"];status=qr["status"]
    cost=br["total_estimated_cost_inr"];issues=br["total_issues"]
    w=min(qr["dimensions"],key=qr["dimensions"].get)
    v,a={"HEALTHY":("is in excellent health","Schedule quarterly reviews to maintain this standard."),"WARNING":("requires immediate attention","Resolve high-severity issues within 48 hours."),"CRITICAL":("is in critical condition","Halt downstream model training. Immediate remediation required.")}.get(status,("requires review","Please investigate."))
    return(f"The dataset <strong style='color:#111827'>{fn}</strong> {v} with a quality score of <strong style='color:{sc(s)}'>{s}/100</strong>. "
           f"<strong>{issues} quality issues</strong> detected, estimated business risk of <strong style='color:#E11D48'>₹{cost:,}</strong>. "
           f"Weakest dimension: <strong>{w.capitalize()}</strong> ({qr['dimensions'][w]}/100). {a}")

def cdims(dims):
    fig,ax=plt.subplots(figsize=(5,2.6));sty(ax,fig)
    lb=[d.capitalize() for d in dims];vl=list(dims.values())
    bars=ax.barh(lb,vl,color=[sc(v) for v in vl],height=0.44)
    ax.set_xlim(0,115)
    for b,v in zip(bars,vl):ax.text(v+1.5,b.get_y()+b.get_height()/2,f'{v}',va='center',fontsize=8.5,color='#374151',fontfamily='monospace',fontweight='bold')
    plt.tight_layout(pad=0.5);return fig

def ccost(issues):
    data=sorted([i for i in issues if i["estimated_cost_inr"]>0],key=lambda x:x["estimated_cost_inr"])[-6:]
    if not data:return None
    fig,ax=plt.subplots(figsize=(5,2.6));sty(ax,fig)
    clrs=["#E11D48" if i["severity"]=="CRITICAL" else "#D97706" if i["severity"]=="HIGH" else "#4F46E5" for i in data]
    ax.barh([i["column"] for i in data],[i["estimated_cost_inr"] for i in data],color=clrs,height=0.44)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_:f'₹{int(x):,}'))
    plt.tight_layout(pad=0.5);return fig

def ctrend(history):
    fig,ax=plt.subplots(figsize=(7,2.8));sty(ax,fig)
    sc_=ax.plot([h["name"][:12] for h in history],[h["score"] for h in history],
                color='#4F46E5',lw=2,marker='o',ms=6,markerfacecolor='white',markeredgewidth=2)
    ax.fill_between([h["name"][:12] for h in history],[h["score"] for h in history],alpha=0.08,color='#4F46E5')
    ax.axhline(95,color='#059669',ls='--',alpha=0.5,lw=1.5)
    ax.axhline(80,color='#D97706',ls='--',alpha=0.5,lw=1.5)
    ax.set_ylim(50,100);plt.xticks(rotation=20,ha='right')
    plt.tight_layout(pad=0.5);return fig

def chist(cd,cn):
    fig,ax=plt.subplots(figsize=(5,2.6));sty(ax,fig)
    ax.hist(cd.dropna(),bins=25,color='#4F46E5',alpha=0.75,edgecolor='white',lw=0.5)
    ax.set_xlabel(cn,fontsize=8,color='#6B7280')
    plt.tight_layout(pad=0.5);return fig

def ddict(df):
    rows=[]
    for col in df.columns:
        np_=round(df[col].isnull().sum()/len(df)*100,1)
        u=df[col].nunique()
        s=f"{df[col].min()} → {df[col].max()}" if df[col].dtype in[np.int64,np.float64] else str(df[col].value_counts().index[0] if not df[col].isnull().all() else "—")
        rows.append({"Column":col,"Type":str(df[col].dtype),"Null %":f"{np_}%","Unique":u,"Range / Top":s})
    return pd.DataFrame(rows)

def pqueue(issues):
    if not issues:return pd.DataFrame()
    dq=pd.DataFrame(issues).sort_values("estimated_cost_inr",ascending=False).reset_index(drop=True)
    dq.index+=1;dq["Cost (₹)"]=dq["estimated_cost_inr"].apply(lambda x:f"₹{x:,}")
    return dq[["severity","rule","column","issue_count","Cost (₹)","recommendation"]].rename(columns={"severity":"Severity","rule":"Rule","column":"Column","issue_count":"Records","recommendation":"Recommended Action"})

# ═══════════════════════════════════════════════════
# NAVBAR
# ═══════════════════════════════════════════════════
st.markdown("""
<div class="navbar">
    <div class="nav-brand">
        <div class="nav-icon">🛡️</div>
        <div>
            <div class="nav-title">DataSentry</div>
            <div class="nav-sub">Enterprise Quality Engine</div>
        </div>
    </div>
    <span class="nav-badge">v2.0</span>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# HERO + FEATURE CARDS (always visible at top)
# ═══════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">🛡️ Data Quality Intelligence</div>
    <h1>Stop trusting data.<br><span class="grad">Start verifying it.</span></h1>
    <p class="hero-sub">Upload any CSV to score data health across 4 dimensions,
    detect anomalies automatically, and quantify the exact rupee cost of every issue found.</p>
    <div class="hero-stats">
        <div>
            <div class="hero-stat-val">0–100</div>
            <div class="hero-stat-label">Health Score</div>
        </div>
        <div>
            <div class="hero-stat-val">4</div>
            <div class="hero-stat-label">Quality Dimensions</div>
        </div>
        <div>
            <div class="hero-stat-val">₹ Cost</div>
            <div class="hero-stat-label">Business Impact</div>
        </div>
        <div>
            <div class="hero-stat-val">Auto</div>
            <div class="hero-stat-label">Dictionary Gen</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Feature Cards
st.markdown("<div style='padding:40px 0 32px'>", unsafe_allow_html=True)
fc1,fc2,fc3,fc4 = st.columns(4)
for col,(icon,title,desc),d in zip([fc1,fc2,fc3,fc4],[
    ("📊","Quality Scoring","4-dimension health score: completeness, uniqueness, validity, consistency."),
    ("💰","Business Impact","Every issue quantified in rupees — not just counts and percentages."),
    ("🔍","Column Deep Dive","Inspect any column with distributions, statistics and null analysis."),
    ("📋","Action Queue","Fix priority list ranked by rupee cost. Know exactly what to fix first."),
],["d1","d2","d3","d4"]):
    col.markdown(f"""
    <div class="feature-card au {d}">
        <div class="feature-icon-wrap">{icon}</div>
        <div class="feature-title">{title}</div>
        <div class="feature-desc">{desc}</div>
    </div>""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# UPLOAD SECTION (below hero and features)
# ═══════════════════════════════════════════════════
st.markdown("""
<div class="upload-section au d3">
    <div class="upload-title">Upload Your Dataset</div>
    <div class="upload-sub">Supports any CSV file — DataSentry adapts to your data automatically.</div>
</div>
""", unsafe_allow_html=True)

uc1,uc2,uc3 = st.columns([2,2,1])
with uc1:
    st.markdown('<span class="sec-label">Primary Dataset</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV",type=["csv"],label_visibility="collapsed",key="primary")
with uc2:
    st.markdown('<span class="sec-label">Compare Dataset (optional)</span>', unsafe_allow_html=True)
    compare_file = st.file_uploader("Second CSV",type=["csv"],label_visibility="collapsed",key="compare")
with uc3:
    st.markdown('<span class="sec-label">Recent Scans</span>', unsafe_allow_html=True)
    if st.session_state.history:
        for h in reversed(st.session_state.history[-3:]):
            c=sc(h["score"])
            st.markdown(f'<div class="hist-row"><span class="hist-name">{h["name"][:16]}</span><span class="hist-score" style="color:{c}">{h["score"]}</span></div>',unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size:.75rem;color:#9CA3AF;margin:8px 0">No scans yet.</p>',unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════
if uploaded_file is not None:
    os.makedirs("data/raw",exist_ok=True)
    tp=f"data/raw/{uploaded_file.name}"
    with open(tp,"wb") as f:f.write(uploaded_file.getbuffer())

    with st.spinner("Running analysis..."):
        df,ing,qr,br=run_analysis(tp,uploaded_file.name)

    score=qr["overall_score"];status=qr["status"]

    st.divider()

    h1,h2=st.columns([5,1])
    with h1:
        st.markdown(f'<div class="page-hdr"><div class="page-title">{uploaded_file.name}</div><div class="page-meta">{len(df):,} records · {len(df.columns)} columns · {datetime.now().strftime("%d %b %Y, %H:%M")}</div></div>',unsafe_allow_html=True)
    with h2:
        st.markdown(f'<div style="text-align:right;padding-top:14px">{badge(status)}</div>',unsafe_allow_html=True)

    k1,k2,k3,k4,k5=st.columns(5)
    for col,(val,lbl,color,d) in zip([k1,k2,k3,k4,k5],[
        (str(score),"Quality Score",sc(score),"d1"),
        (f"₹{br['total_estimated_cost_inr']:,}","Cost at Risk","#E11D48","d2"),
        (str(br['total_issues']),"Total Anomalies","#111827","d3"),
        (str(br['critical_issues']),"Critical Issues","#E11D48","d4"),
        (str(br['high_issues']),"High Severity","#D97706","d5"),
    ]):
        col.markdown(f'<div class="kpi au {d}"><div class="kpi-val" style="color:{color}">{val}</div><div class="kpi-lbl">{lbl}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    t1,t2,t3,t4,t5,t6=st.tabs(["Overview","Deep Dive","Business Impact","Action Queue","Data Dictionary","Trend"])

    with t1:
        cl,cr=st.columns(2)
        with cl:
            st.markdown('<div class="sec-title">Quality Dimensions</div>',unsafe_allow_html=True)
            st.pyplot(cdims(qr["dimensions"]),use_container_width=True)
        with cr:
            st.markdown('<div class="sec-title">Cost by Column</div>',unsafe_allow_html=True)
            fc=ccost(br["issues"])
            if fc:st.pyplot(fc,use_container_width=True)
            else:st.success("No cost-bearing issues detected.")
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="sec-title">Executive Summary</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="exec-box">{summary(qr,br,uploaded_file.name)}</div>',unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="sec-title">Column Inspector</div>',unsafe_allow_html=True)
        sel=st.selectbox("Column",df.columns.tolist(),label_visibility="collapsed")
        cd=df[sel]
        m1,m2,m3,m4=st.columns(4)
        m1.metric("Missing",int(cd.isnull().sum()))
        m2.metric("Missing %",f"{round(cd.isnull().sum()/len(df)*100,2)}%")
        m3.metric("Unique",int(cd.nunique()))
        m4.metric("Type",str(cd.dtype))
        st.markdown("<br>",unsafe_allow_html=True)
        if cd.dtype in[np.int64,np.float64]:
            dl,dr=st.columns(2)
            with dl:
                st.markdown('<div class="sec-title">Distribution</div>',unsafe_allow_html=True)
                st.pyplot(chist(cd,sel),use_container_width=True)
            with dr:
                st.markdown('<div class="sec-title">Statistics</div>',unsafe_allow_html=True)
                st.dataframe(cd.describe().round(2).to_frame().rename(columns={sel:"Value"}),use_container_width=True)
        else:
            st.markdown('<div class="sec-title">Top Values</div>',unsafe_allow_html=True)
            vc=cd.value_counts().head(10).reset_index();vc.columns=["Value","Frequency"]
            st.dataframe(vc,use_container_width=True,hide_index=True)

    with t3:
        st.markdown('<div class="sec-title">Issue Breakdown — Ranked by Business Cost</div>',unsafe_allow_html=True)
        if br["issues"]:
            for i,issue in enumerate(sorted(br["issues"],key=lambda x:x["estimated_cost_inr"],reverse=True)):
                sev=issue["severity"].lower()
                dd=f"d{min(i+1,5)}"
                st.markdown(f"""
                <div class="issue-card {sev} au {dd}">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <span class="issue-rule">{issue['rule']}</span>
                            <span class="issue-col">{issue['column']}</span>
                        </div>
                        <span class="issue-cost">₹{issue['estimated_cost_inr']:,}</span>
                    </div>
                    <div class="issue-rec">{issue['recommendation']}</div>
                    <div class="issue-meta">{issue['issue_count']:,} impacted records · {issue['severity']}</div>
                </div>""",unsafe_allow_html=True)
        else:
            st.success("No critical issues detected. Data integrity is optimal.")

    with t4:
        st.markdown('<div class="sec-title">Fix Priority Queue</div>',unsafe_allow_html=True)
        pq=pqueue(br["issues"])
        if not pq.empty:
            st.dataframe(pq,use_container_width=True)
            st.info("Fix from top to bottom. Highest cost issues protect the most business value.")
        else:
            st.success("No pending actions. All checks passed.")

    with t5:
        st.markdown('<div class="sec-title">Auto-Generated Data Dictionary</div>',unsafe_allow_html=True)
        dd=ddict(df)
        st.dataframe(dd,use_container_width=True,hide_index=True)
        st.markdown("<br>",unsafe_allow_html=True)
        buf=io.StringIO();dd.to_csv(buf,index=False)
        st.download_button("⬇️ Export Data Dictionary",data=buf.getvalue(),file_name=f"datasentry_dict_{uploaded_file.name}",mime="text/csv")

    with t6:
        st.markdown('<div class="sec-title">Quality Score Trend</div>',unsafe_allow_html=True)
        if len(st.session_state.history)>1:
            st.pyplot(ctrend(st.session_state.history),use_container_width=True)
            st.markdown('<p style="font-size:.75rem;color:#6B7280;font-weight:500">Green = Healthy (95+) · Yellow = Warning (80+)</p>',unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(st.session_state.history),use_container_width=True,hide_index=True)
        else:
            st.info("Upload multiple datasets to track score trends.")

    if compare_file is not None:
        st.divider()
        st.markdown('<div class="sec-title">Dataset Comparison</div>',unsafe_allow_html=True)
        tp2=f"data/raw/{compare_file.name}"
        with open(tp2,"wb") as f:f.write(compare_file.getbuffer())
        with st.spinner("Analyzing second dataset..."):
            df2,_,qr2,br2=run_analysis(tp2,compare_file.name)
        cc1,cc2=st.columns(2)
        for col,name,q,b in[(cc1,uploaded_file.name,qr,br),(cc2,compare_file.name,qr2,br2)]:
            with col:
                st.markdown(f'<div class="sec-title">{name}</div>',unsafe_allow_html=True)
                st.metric("Quality Score",f"{q['overall_score']}/100")
                st.metric("Issues Found",b["total_issues"])
                st.metric("Cost at Risk",f"₹{b['total_estimated_cost_inr']:,}")

    with st.expander("Inspect Raw Data"):
        st.dataframe(df.head(50),use_container_width=True)
    with st.expander("Ingestion Telemetry"):
        st.json(ing)

st.markdown("""
<div class="footer">
    <p>DataSentry v2.0 · Built by Nawaz · Enterprise Data Quality Platform</p>
</div>
""", unsafe_allow_html=True)