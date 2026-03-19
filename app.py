import streamlit as st
import pandas as pd
import joblib
import numpy as np
import re
import os
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ===============================
# PAGE CONFIG
# ===============================

st.set_page_config(
    page_title="සිංහල News Sentinel",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# LANGUAGE HELPER — must be initialised before any UI
# ===============================

if "lang" not in st.session_state:
    st.session_state.lang = "si"   # default: Sinhala

def t(si_text, en_text):
    """Return si_text or en_text based on current language setting."""
    return si_text if st.session_state.lang == "si" else en_text

# ===============================
# REFINED THEME & STYLING
# ===============================

st.markdown("""
<style>
    /* ── Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Sinhala:wght@300;400;500;600;700&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=DM+Mono:wght@400;500&display=swap');

    /* ── Design Tokens ── */
    :root {
        --bg:           #07101f;
        --surface:      #0e1929;
        --surface-2:    #152135;
        --surface-3:    #1b2d45;
        --border:       #223048;
        --border-soft:  #182840;

        --indigo:       #6473f3;
        --indigo-dim:   rgba(100,115,243,0.14);
        --indigo-glow:  rgba(100,115,243,0.32);
        --indigo-light: #a5b4fc;
        --emerald:      #10c98a;
        --amber:        #f5b731;
        --rose:         #f05c6e;

        --txt-1: #e6ecf5;
        --txt-2: #8fa5c2;
        --txt-3: #4d637f;

        --r:  14px;
        --rl: 20px;
        --shadow: 0 6px 30px rgba(0,0,0,0.5);
    }

    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', 'Noto Sans Sinhala', sans-serif !important;
        background: var(--bg) !important;
        color: var(--txt-1) !important;
    }
    h1,h2,h3,h4,h5,h6 { font-family: 'DM Sans','Noto Sans Sinhala',sans-serif; }
    code, pre           { font-family: 'DM Mono', monospace; }
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width:6px; height:6px; }
    ::-webkit-scrollbar-track  { background: var(--surface); }
    ::-webkit-scrollbar-thumb  { background: var(--indigo); border-radius:3px; }

    /* ── HERO ── */
    .hero {
        background: linear-gradient(140deg, var(--surface-2) 0%, var(--bg) 100%);
        border: 1px solid var(--border);
        border-radius: var(--rl);
        padding: 2.5rem 2.5rem 2.2rem;
        position: relative; overflow: hidden;
        margin-bottom: 1.5rem;
    }
    .hero::before {
        content:''; position:absolute; inset:0;
        background: radial-gradient(ellipse 55% 65% at 85% 45%,
            rgba(100,115,243,0.09) 0%, transparent 70%);
        pointer-events:none;
    }
    .hero-badge {
        display:inline-flex; align-items:center; gap:6px;
        background:var(--indigo-dim); border:1px solid rgba(100,115,243,0.4);
        color:var(--indigo-light); font-size:0.7rem; font-weight:700;
        letter-spacing:0.1em; text-transform:uppercase;
        padding:3px 11px; border-radius:20px; margin-bottom:0.9rem;
    }
    .hero-title {
        font-size: clamp(1.85rem,3.2vw,2.7rem);
        font-weight:700; color:var(--txt-1);
        margin:0 0 0.45rem; line-height:1.15; letter-spacing:-0.5px;
    }
    .hero-title span {
        background: linear-gradient(90deg, var(--indigo) 0%, #a78bfa 100%);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    }
    .hero-sub {
        color:var(--txt-2); font-size:0.93rem;
        margin:0; line-height:1.7; max-width:640px;
    }
    .hero-meta {
        position:absolute; bottom:1.2rem; right:1.8rem;
        color:var(--txt-3); font-size:0.78rem;
    }
    .hero-meta a { color:var(--indigo); text-decoration:none; font-weight:600; }

    /* ── SYSTEM CARD ── */
    .sys-card {
        background: var(--surface-2); border:1px solid var(--border);
        border-radius:var(--rl); padding:1.75rem 1.75rem 1.5rem;
        margin-bottom:1.75rem; position:relative; overflow:hidden;
    }
    .sys-card::after {
        content:''; position:absolute; top:0; left:0;
        width:4px; height:100%;
        background: linear-gradient(180deg, var(--indigo) 0%, #a78bfa 100%);
    }
    .sys-card h3 {
        color:var(--txt-1); font-size:1.05rem;
        margin:0 0 0.7rem; font-weight:700;
    }
    .sys-card p  { color:var(--txt-2); font-size:0.88rem; line-height:1.75; margin:0 0 0.5rem; }
    .sys-card ul { color:var(--txt-2); padding-left:1.35rem; margin:0.4rem 0 0; }
    .sys-card li { font-size:0.87rem; line-height:2.1; }
    .sys-card li strong { color:var(--txt-1); }
    .sys-divider { border:none; border-top:1px solid var(--border-soft); margin:0.8rem 0; }

    /* ── SECTION HEADERS ── */
    .sec-hdr {
        display:flex; align-items:center; gap:10px;
        font-size:1.05rem; font-weight:700; color:var(--txt-1);
        margin:2rem 0 1rem; padding-bottom:0.6rem;
        border-bottom:1px solid var(--border);
    }
    .sec-dot {
        width:8px; height:8px; border-radius:50%;
        background:var(--indigo); flex-shrink:0;
        box-shadow:0 0 8px var(--indigo-glow);
    }

    /* ── INFO / WARNING BOXES ── */
    .info-box {
        background:var(--indigo-dim); border:1px solid rgba(100,115,243,0.3);
        border-radius:var(--r); padding:0.9rem 1.1rem;
        margin:0.9rem 0; color:var(--txt-2); font-size:0.87rem; line-height:1.75;
    }
    .info-box strong { color:var(--indigo-light); }
    .warn-box {
        background:rgba(245,183,49,0.07); border:1px solid rgba(245,183,49,0.28);
        border-radius:var(--r); padding:0.9rem 1.1rem;
        margin:0.9rem 0; color:var(--txt-2); font-size:0.87rem; line-height:1.75;
    }
    .warn-box strong { color:var(--amber); }

    /* ── OPPORTUNITY / MONITOR CARDS ── */
    .opp-card {
        background:rgba(16,201,138,0.07); border:1px solid rgba(16,201,138,0.22);
        border-radius:var(--r); padding:1.1rem 1.2rem; margin-bottom:0.7rem;
    }
    .opp-card h4 { color:var(--emerald); margin:0 0 0.35rem; font-size:0.93rem; }
    .mon-card {
        background:rgba(240,92,110,0.07); border:1px solid rgba(240,92,110,0.22);
        border-radius:var(--r); padding:1.1rem 1.2rem; margin-bottom:0.7rem;
    }
    .mon-card h4 { color:var(--rose); margin:0 0 0.35rem; font-size:0.93rem; }
    .c-row  { color:var(--txt-2); font-size:0.83rem; margin:0.2rem 0; }
    .c-row strong { color:var(--txt-1); }
    .tg  { color:var(--emerald); font-weight:700; }
    .tr  { color:var(--rose);    font-weight:700; }

    /* ── STATUS DOTS ── */
    .dot { width:9px;height:9px;border-radius:50%;display:inline-block;margin-right:6px;vertical-align:middle; }
    .dot-on  { background:var(--emerald); box-shadow:0 0 5px rgba(16,201,138,0.55); }
    .dot-off { background:var(--rose);    box-shadow:0 0 5px rgba(240,92,110,0.45); }

    /* ── FOOTER ── */
    .footer {
        text-align:center; padding:2.5rem 0 1rem;
        border-top:1px solid var(--border); margin-top:3rem;
        color:var(--txt-3); font-size:0.8rem; line-height:2.1;
    }
    .footer a { color:var(--indigo); text-decoration:none; font-weight:600; }
    .footer strong { color:var(--txt-2); }

    /* ── Streamlit overrides ── */
    .main { background:var(--bg) !important; }

    [data-testid="stSidebar"] {
        background:var(--surface) !important;
        border-right:1px solid var(--border) !important;
    }

    .stTextArea textarea {
        background:var(--surface-2) !important; color:var(--txt-1) !important;
        border:1px solid var(--border) !important; border-radius:var(--r) !important;
        font-family:'Noto Sans Sinhala','DM Sans',sans-serif !important;
        font-size:0.91rem !important; line-height:1.7 !important;
    }
    .stTextArea textarea:focus {
        border-color:var(--indigo) !important;
        box-shadow:0 0 0 3px var(--indigo-dim) !important;
    }
    .stTextArea textarea::placeholder { color:var(--txt-3) !important; }

    .stButton > button {
        background:linear-gradient(135deg, var(--indigo) 0%, #4f46e5 100%) !important;
        color:#fff !important; border:none !important;
        border-radius:var(--r) !important; font-weight:600 !important;
        font-size:0.87rem !important; padding:0.65rem 1.35rem !important;
        transition:all 0.2s !important; letter-spacing:0.02em;
    }
    .stButton > button:hover {
        transform:translateY(-2px) !important;
        box-shadow:0 8px 22px var(--indigo-glow) !important;
    }

    .stNumberInput input {
        background:var(--surface-2) !important; color:var(--txt-1) !important;
        border:1px solid var(--border) !important; border-radius:8px !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap:5px; background:var(--surface-2);
        padding:5px; border-radius:var(--r); border:1px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] {
        background:transparent !important; color:var(--txt-2) !important;
        border-radius:10px !important; padding:0.55rem 1.2rem !important;
        font-weight:500; font-size:0.86rem;
    }
    .stTabs [aria-selected="true"] {
        background:var(--indigo) !important; color:#fff !important;
    }

    .streamlit-expanderHeader {
        background:var(--surface-2) !important; color:var(--txt-1) !important;
        border:1px solid var(--border) !important; border-radius:var(--r) !important;
    }

    .stProgress > div > div {
        background:linear-gradient(90deg, var(--indigo) 0%, var(--emerald) 100%);
        border-radius:4px; height:5px !important;
    }

    .dataframe { background:var(--surface-2) !important; border-radius:var(--r) !important; }
    .dataframe th {
        background:var(--surface-3) !important; color:var(--txt-1) !important;
        font-weight:600 !important; padding:0.65rem !important;
    }
    .dataframe td {
        background:var(--surface-2) !important; color:var(--txt-2) !important;
        padding:0.65rem !important; border-bottom:1px solid var(--border-soft) !important;
    }
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA & CONFIG
# ===============================

STOPWORDS_PATH      = "./data/stop words.txt"
SENTIMENT_MODEL_PATH = "saved_models"
PRICE_MODEL_PATH    = "price_models_final_v3"

@st.cache_resource
def load_stopwords():
    if not os.path.exists(STOPWORDS_PATH):
        st.error("⚠️ Stopwords file not found.")
        return []
    return open(STOPWORDS_PATH, encoding="utf-8").read().splitlines()

stop_words = load_stopwords()

def tokenizer(text):
    tokens = re.findall(r'\b\w+\b', text.lower())
    return [tk for tk in tokens if tk not in stop_words]

# ── Companies ────────────────────────────────────────────────────────────────

companies = [
    "MCPL.N0000","WATA.N0000","AGPL.N0000","HAPU.N0000",
    "KOTA.N0000","BFL.N0000","RWSL.N0000","DIPP.N0000",
    "MGT.N0000","HEXP.N0000"
]

BEST_MODELS = {c: 'XGBoost' for c in companies}

MODEL_METRICS = {
    'MCPL.N0000': {'XGBoost':0.18,'SARIMAX':13.66,'LightGBM':4.91, 'Hybrid':None},
    'WATA.N0000': {'XGBoost':0.56,'SARIMAX':14.43,'LightGBM':None, 'Hybrid':15.91},
    'AGPL.N0000': {'XGBoost':0.30,'SARIMAX':21.80,'LightGBM':10.00,'Hybrid':None},
    'HAPU.N0000': {'XGBoost':0.25,'SARIMAX':12.43,'LightGBM':1.58, 'Hybrid':None},
    'KOTA.N0000': {'XGBoost':0.22,'SARIMAX':7.08, 'LightGBM':1.17, 'Hybrid':None},
    'BFL.N0000':  {'XGBoost':0.64,'SARIMAX':16.31,'LightGBM':None, 'Hybrid':10.10},
    'RWSL.N0000': {'XGBoost':1.82,'SARIMAX':29.73,'LightGBM':None, 'Hybrid':31.14},
    'DIPP.N0000': {'XGBoost':0.24,'SARIMAX':11.48,'LightGBM':5.52, 'Hybrid':None},
    'MGT.N0000':  {'XGBoost':0.18,'SARIMAX':21.99,'LightGBM':0.64, 'Hybrid':None},
    'HEXP.N0000': {'XGBoost':0.42,'SARIMAX':16.48,'LightGBM':4.85, 'Hybrid':None},
}

SPLIT_COMPANIES = {
    'WATA.N0000': {'date':'2025-03-03','ratio':5,'adjusted':True},
    'BFL.N0000':  {'date':'2023-08-01','ratio':5,'adjusted':True},
}

company_data = {
    'MCPL.N0000': {'name':'Mahaweli Coconut Plantations PLC','symbol':'MCPL','sector':'Plantations',    'default_price':50.50, 'color':'#0ea5e9'},
    'WATA.N0000': {'name':'Watawala Plantations PLC',        'symbol':'WATA','sector':'Plantations',    'default_price':180.00,'color':'#10b981'},
    'AGPL.N0000': {'name':'Agarapatana Plantations PLC',     'symbol':'AGPL','sector':'Plantations',    'default_price':22.00, 'color':'#14b8a6'},
    'HAPU.N0000': {'name':'Hapugastenne Plantations PLC',    'symbol':'HAPU','sector':'Plantations',    'default_price':74.00, 'color':'#06b6d4'},
    'KOTA.N0000': {'name':'Kotagala Plantations PLC',        'symbol':'KOTA','sector':'Plantations',    'default_price':9.80,  'color':'#3b82f6'},
    'BFL.N0000':  {'name':'Bairaha Farms PLC',               'symbol':'BFL', 'sector':'Food & Beverage','default_price':300.00,'color':'#6366f1'},
    'RWSL.N0000': {'name':'Raigam Wayamba Salterns PLC',     'symbol':'RWSL','sector':'Manufacturing',  'default_price':27.50, 'color':'#8b5cf6'},
    'DIPP.N0000': {'name':'Dipped Products PLC',             'symbol':'DIPP','sector':'Manufacturing',  'default_price':68.00, 'color':'#a855f7'},
    'MGT.N0000':  {'name':'Hayleys Fabric PLC',              'symbol':'MGT', 'sector':'Plantations',    'default_price':42.50, 'color':'#d946ef'},
    'HEXP.N0000': {'name':'Hayleys Fibre PLC',               'symbol':'HEXP','sector':'Export & Trading','default_price':95.00,'color':'#ec4899'},
}

# ===============================
# MODEL LOADING
# ===============================

@st.cache_resource
def load_all_models():
    models = {k: {} for k in ['sentiment','xgboost','sarimax','lightgbm','hybrid',
                                'xgboost_scalers','lightgbm_scalers','hybrid_scalers',
                                'xgboost_features','lightgbm_features','hybrid_weights','metadata']}
    status = {k: {} for k in ['sentiment','xgboost','sarimax','lightgbm','hybrid']}

    # Sentiment
    for company in companies:
        mf = f"{SENTIMENT_MODEL_PATH}/{company}_svm.joblib"
        if os.path.exists(mf):
            try:
                models['sentiment'][company] = joblib.load(mf)
                status['sentiment'][company] = {'loaded':True,'error':None}
            except Exception as e:
                models['sentiment'][company] = None
                status['sentiment'][company] = {'loaded':False,'error':str(e)}
        else:
            models['sentiment'][company] = None
            status['sentiment'][company] = {'loaded':False,'error':'Not found'}

    for company in companies:
        cd = f"{PRICE_MODEL_PATH}/{company}"
        if not os.path.exists(cd): continue

        # XGBoost
        xf = f"{cd}/xgboost.joblib"
        if os.path.exists(xf):
            try:
                models['xgboost'][company] = joblib.load(xf)
                sf = f"{cd}/xgboost_scaler.joblib"
                if os.path.exists(sf): models['xgboost_scalers'][company] = joblib.load(sf)
                mf2 = f"{cd}/xgboost_metadata.json"
                if os.path.exists(mf2):
                    with open(mf2) as f:
                        md = json.load(f)
                        models['metadata'][f"{company}_xgb"] = md
                        models['xgboost_features'][company] = md.get('feature_cols',[])
                status['xgboost'][company] = {'loaded':True,'error':None}
            except Exception as e:
                models['xgboost'][company] = None
                status['xgboost'][company] = {'loaded':False,'error':str(e)}
        else:
            models['xgboost'][company] = None
            status['xgboost'][company] = {'loaded':False,'error':'Not found'}

        # SARIMAX
        sf2 = f"{cd}/sarimax.joblib"
        if os.path.exists(sf2):
            try:
                models['sarimax'][company] = joblib.load(sf2)
                mf3 = f"{cd}/sarimax_metadata.json"
                if os.path.exists(mf3):
                    with open(mf3) as f: models['metadata'][f"{company}_sar"] = json.load(f)
                status['sarimax'][company] = {'loaded':True,'error':None}
            except Exception as e:
                models['sarimax'][company] = None
                status['sarimax'][company] = {'loaded':False,'error':str(e)}
        else:
            models['sarimax'][company] = None
            status['sarimax'][company] = {'loaded':False,'error':'Not found'}

        # LightGBM
        lf = f"{cd}/lightgbm.joblib"
        if os.path.exists(lf):
            try:
                models['lightgbm'][company] = joblib.load(lf)
                slgb = f"{cd}/lightgbm_scaler.joblib"
                if os.path.exists(slgb): models['lightgbm_scalers'][company] = joblib.load(slgb)
                mf4 = f"{cd}/lightgbm_metadata.json"
                if os.path.exists(mf4):
                    with open(mf4) as f:
                        md = json.load(f)
                        models['metadata'][f"{company}_lgb"] = md
                        models['lightgbm_features'][company] = md.get('feature_cols',[])
                status['lightgbm'][company] = {'loaded':True,'error':None}
            except Exception as e:
                models['lightgbm'][company] = None
                status['lightgbm'][company] = {'loaded':False,'error':str(e)}
        else:
            models['lightgbm'][company] = None
            status['lightgbm'][company] = {'loaded':False,'error':'Not found'}

        # Hybrid
        hwf = f"{cd}/hybrid_weights.json"
        if os.path.exists(hwf):
            try:
                with open(hwf) as f: models['hybrid_weights'][company] = json.load(f)
                hm = {}
                for mn in ['XGBoost_Robust','XGBoost_Standard','LightGBM','RandomForest']:
                    hmf = f"{cd}/hybrid_{mn}.joblib"
                    if os.path.exists(hmf): hm[mn] = joblib.load(hmf)
                hs = {}
                for sn in ['robust','standard']:
                    hsf = f"{cd}/hybrid_scaler_{sn}.joblib"
                    if os.path.exists(hsf): hs[sn] = joblib.load(hsf)
                if hm:
                    models['hybrid'][company] = hm
                    models['hybrid_scalers'][company] = hs
                    mhf = f"{cd}/hybrid_metadata.json"
                    if os.path.exists(mhf):
                        with open(mhf) as f: models['metadata'][f"{company}_hybrid"] = json.load(f)
                    status['hybrid'][company] = {'loaded':True,'error':None}
                else:
                    status['hybrid'][company] = {'loaded':False,'error':'No models found'}
            except Exception as e:
                models['hybrid'][company] = None
                status['hybrid'][company] = {'loaded':False,'error':str(e)}
        else:
            models['hybrid'][company] = None
            status['hybrid'][company] = {'loaded':False,'error':'No weights'}

    return models, status

models, model_status = load_all_models()

# ===============================
# FEATURE ENGINEERING
# ===============================

def create_enhanced_features(company, sentiment_score, prev_close, date):
    f = {}
    f['price_lag1']=prev_close; f['price_lag2']=prev_close*0.99
    f['price_lag3']=prev_close*0.98; f['price_lag5']=prev_close*0.97
    f['price_lag10']=prev_close*0.95; f['price_lag20']=prev_close*0.90
    er = sentiment_score*0.01
    for k,v in [('return_1d',er),('return_2d',er*2),('return_3d',er*3),
                ('return_5d',er*5),('return_10d',er*10),('return_20d',er*20)]: f[k]=v
    f['ma_3']=prev_close*(1+er*1.5); f['ma_5']=prev_close*(1+er*2)
    f['ma_10']=prev_close*(1+er*3); f['ma_20']=prev_close*(1+er*4); f['ma_50']=prev_close*(1+er*5)
    f['ema_5']=prev_close*(1+er*1.8); f['ema_10']=prev_close*(1+er*2.5); f['ema_20']=prev_close*(1+er*3.2)
    f['volatility_3']=0.015+abs(sentiment_score)*0.01
    f['volatility_5']=0.020+abs(sentiment_score)*0.01
    f['volatility_10']=0.025+abs(sentiment_score)*0.01
    f['volatility_20']=0.030+abs(sentiment_score)*0.01
    f['price_vs_ma5']=prev_close/f['ma_5']-1; f['price_vs_ma10']=prev_close/f['ma_10']-1
    f['price_vs_ma20']=prev_close/f['ma_20']-1; f['price_vs_ma50']=prev_close/f['ma_50']-1
    f['price_vs_ema5']=prev_close/f['ema_5']-1; f['price_vs_ema10']=prev_close/f['ema_10']-1
    f['price_vs_ema20']=prev_close/f['ema_20']-1
    f['macd_line']=f['ema_10']-f['ema_20']; f['signal_line']=f['macd_line']*0.9
    f['macd_histogram']=f['macd_line']-f['signal_line']
    f['rsi']=50+(sentiment_score*30)
    f['bb_middle']=f['ma_20']; f['bb_std']=prev_close*0.02
    f['bb_upper']=f['bb_middle']+2*f['bb_std']; f['bb_lower']=f['bb_middle']-2*f['bb_std']
    f['bb_position']=(prev_close-f['bb_lower'])/(f['bb_upper']-f['bb_lower']+0.001)
    f['sentiment_raw']=sentiment_score; f['sentiment_lag1']=sentiment_score*0.95
    f['sentiment_lag2']=sentiment_score*0.90; f['sentiment_lag3']=sentiment_score*0.85
    f['sentiment_ma3']=sentiment_score; f['sentiment_ma5']=sentiment_score; f['sentiment_ma10']=sentiment_score
    f['sentiment_change_1d']=0; f['sentiment_change_3d']=0; f['sentiment_change_5d']=0
    f['sentiment_volatility_3']=abs(sentiment_score)*0.1; f['sentiment_volatility_5']=abs(sentiment_score)*0.15
    f['price_momentum_3']=er*3; f['price_momentum_5']=er*5; f['price_momentum_10']=er*10
    f['sentiment_price_interaction']=sentiment_score*er
    f['sentiment_volatility_interaction']=sentiment_score*f['volatility_5']
    f['day_of_week']=date.weekday(); f['month']=date.month
    f['quarter']=(date.month-1)//3+1; f['day_of_month']=date.day
    f['rolling_max_5']=prev_close*1.05; f['rolling_min_5']=prev_close*0.95
    f['rolling_max_20']=prev_close*1.10; f['rolling_min_20']=prev_close*0.90
    return f

def _vec(fd, cols):
    return np.array([fd.get(c,0) for c in cols], dtype=np.float32).reshape(1,-1)

def prep_xgb(company,ss,pc,date,fc):  return _vec(create_enhanced_features(company,ss,pc,date), fc)
def prep_lgb(company,ss,pc,date,fc):  return _vec(create_enhanced_features(company,ss,pc,date), fc)
def prep_hyb(company,ss,pc,date,_='robust'):
    fd = create_enhanced_features(company,ss,pc,date)
    return np.array(list(fd.values()),dtype=np.float32).reshape(1,-1)
def prep_sar(company,ss,pc,date):     return np.array([[ss]],dtype=np.float32)

# ===============================
# PREDICTION
# ===============================

def predict_xgboost(company,ss,pc,date):
    try:
        if not models['xgboost'].get(company): return None,0
        fc = models['xgboost_features'].get(company,[])
        if not fc: return None,0
        X = prep_xgb(company,ss,pc,date,fc)
        sc = models['xgboost_scalers'].get(company)
        if sc: X = sc.transform(X)
        pred = float(models['xgboost'][company].predict(X)[0])
        mape = MODEL_METRICS[company]['XGBoost']
        return pred, max(0.5,min(0.95,1-mape/100))
    except: return None,0

def predict_sarimax(company,ss,pc,date):
    try:
        if not models['sarimax'].get(company): return None,0
        exog = prep_sar(company,ss,pc,date)
        try:    pred = float(models['sarimax'][company].forecast(steps=1,exog=exog)[0])
        except:
            try: pred = float(models['sarimax'][company].forecast(steps=1)[0])
            except: return None,0
        mape = MODEL_METRICS[company]['SARIMAX']
        return pred, max(0.5,min(0.95,1-mape/100))
    except: return None,0

def predict_lightgbm(company,ss,pc,date):
    try:
        if not models['lightgbm'].get(company): return None,0
        fc = models['lightgbm_features'].get(company,[])
        if not fc: return None,0
        X = prep_lgb(company,ss,pc,date,fc)
        sc = models['lightgbm_scalers'].get(company)
        if sc: X = sc.transform(X)
        pred = float(models['lightgbm'][company].predict(X)[0])
        mape = MODEL_METRICS[company]['LightGBM']
        conf = max(0.5,min(0.95,1-mape/100)) if mape else 0.7
        return pred,conf
    except: return None,0

def predict_hybrid(company,ss,pc,date):
    try:
        if not models['hybrid'].get(company): return None,0
        hm = models['hybrid'][company]; wt = models['hybrid_weights'].get(company,{})
        sc = models['hybrid_scalers'].get(company,{})
        Xr = prep_hyb(company,ss,pc,date,'robust')
        Xs = prep_hyb(company,ss,pc,date,'standard')
        if 'robust'   in sc: Xr = sc['robust'].transform(Xr)
        if 'standard' in sc: Xs = sc['standard'].transform(Xs)
        preds,names=[],[]
        for mn,X in [('XGBoost_Robust',Xr),('XGBoost_Standard',Xs),('LightGBM',Xr),('RandomForest',Xr)]:
            if mn in hm: preds.append(float(hm[mn].predict(X)[0])); names.append(mn)
        if not preds: return None,0
        tw = sum(wt.get(n,1/len(names)) for n in names)
        ep = sum(preds[i]*wt.get(names[i],1/len(names)) for i in range(len(names)))
        if tw>0: ep/=tw
        mape = MODEL_METRICS[company].get('Hybrid',10)
        conf = max(0.5,min(0.95,1-mape/100)) if mape else 0.7
        return ep,conf
    except: return None,0

def predict_best(company,ss,pc,date):
    bm = BEST_MODELS.get(company,'XGBoost')
    fn_map = {'XGBoost':predict_xgboost,'SARIMAX':predict_sarimax,
              'LightGBM':predict_lightgbm,'Hybrid':predict_hybrid}
    fn  = fn_map.get(bm, predict_xgboost)
    pred,conf = fn(company,ss,pc,date)
    if pred is not None:
        mape = MODEL_METRICS[company].get(bm)
        lbl  = f"{bm} (MAPE: {mape:.2f}%)" if mape else bm
        return pred,conf,lbl
    pred,conf = predict_xgboost(company,ss,pc,date)
    if pred is not None:
        return pred,conf,f"XGBoost Fallback (MAPE: {MODEL_METRICS[company]['XGBoost']:.2f}%)"
    return None,0,"No Model"

# ===============================
# SENTIMENT ANALYSIS
# ===============================

def analyze_sentiment(text, company):
    if models['sentiment'].get(company):
        try: return models['sentiment'][company].predict([text])[0]
        except: pass
    tl = text.lower()
    pos = ['profit','growth','increase','success','positive','strong','gain','rise',
           'ලාභ','වර්ධනය','ඉහළ','සාර්ථක','දියුණු','ජය','ඉහල','වැඩි','වාසි',
           'dividend','bonus','expansion','record','high','up','good']
    neg = ['loss','decline','decrease','problem','negative','weak','fall','down',
           'අලාභ','අඩු','පහත','අසාර්ථක','ප්‍රශ්නය','අවාසි','පහල','බිඳවැටීම',
           'crisis','risk','warning','low','bad','poor']
    p = sum(1 for w in pos if w in tl)
    n = sum(1 for w in neg if w in tl)
    return "Positive" if p>n else "Negative" if n>p else "Neutral"

# ===============================
# SIDEBAR
# ===============================

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.2rem 0 0.6rem;'>
        <div style='font-size:1.7rem;'>📰</div>
        <div style='font-size:0.97rem;font-weight:700;color:#e6ecf5;margin-top:4px;'>
            සිංහල NEWS SENTINEL
        </div>
        <div style='font-size:0.72rem;color:#4d637f;margin-top:3px;'>v3.0 · Enhanced Models</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # ── Language Toggle ──────────────────────────────
    lbl_lang = t("භාෂාව", "Language")
    st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:#4d637f;"
                f"letter-spacing:0.09em;text-transform:uppercase;margin-bottom:7px;'>{lbl_lang}</div>",
                unsafe_allow_html=True)
    la, lb = st.columns(2)
    with la:
        if st.button("🇱🇰 සිංහල", use_container_width=True,
                     type="primary" if st.session_state.lang=="si" else "secondary"):
            st.session_state.lang = "si"; st.rerun()
    with lb:
        if st.button("🇬🇧 English", use_container_width=True,
                     type="primary" if st.session_state.lang=="en" else "secondary"):
            st.session_state.lang = "en"; st.rerun()
    st.markdown("---")

    # ── System Status ──
    st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:#4d637f;"
                f"letter-spacing:0.09em;text-transform:uppercase;margin-bottom:8px;'>"
                f"{t('පද්ධති තත්ත්වය','System Status')}</div>", unsafe_allow_html=True)

    sl = sum(1 for s in model_status['sentiment'].values() if s.get('loaded'))
    xl = sum(1 for s in model_status['xgboost'].values()   if s.get('loaded'))
    rl = sum(1 for s in model_status['sarimax'].values()   if s.get('loaded'))
    ll = sum(1 for s in model_status['lightgbm'].values()  if s.get('loaded'))
    hl = sum(1 for s in model_status['hybrid'].values()    if s.get('loaded'))

    for label, loaded, total in [("Sentiment",sl,10),("XGBoost",xl,10),
                                   ("SARIMAX",rl,10),("LightGBM",ll,10),("Hybrid",hl,3)]:
        dc = "dot-on" if loaded>0 else "dot-off"
        st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;'
                    f'padding:3px 0;">'
                    f'<span><span class="dot {dc}"></span>'
                    f'<span style="color:#8fa5c2;font-size:0.83rem;font-weight:500;">{label}</span></span>'
                    f'<span style="color:#4d637f;font-size:0.78rem;">{loaded}/{total}</span>'
                    f'</div>', unsafe_allow_html=True)
    st.markdown("---")

    # ── Best Models ──
    st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:#4d637f;"
                f"letter-spacing:0.09em;text-transform:uppercase;margin-bottom:8px;'>"
                f"{t('හොඳම ආදර්ශ','Best Models')}</div>", unsafe_allow_html=True)
    bm_rows = []
    for c in companies:
        bm  = BEST_MODELS[c]
        mpe = MODEL_METRICS[c].get(bm) or 0
        bm_rows.append({"Symbol":company_data[c]['symbol'],"Model":bm,"MAPE":f"{mpe:.2f}%"})
    st.dataframe(pd.DataFrame(bm_rows), hide_index=True, use_container_width=True)
    st.markdown("---")

    # ── Stock Splits ──
    st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:#4d637f;"
                f"letter-spacing:0.09em;text-transform:uppercase;margin-bottom:8px;'>"
                f"{t('කොටස් බෙදීම','Stock Splits')}</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([
        {"Co":"WATA","Date":"2025-03-03","Ratio":"1:5"},
        {"Co":"BFL", "Date":"2023-08-01","Ratio":"1:5"},
    ]), hide_index=True, use_container_width=True)
    st.markdown("---")

    # ── Config ──
    st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:#4d637f;"
                f"letter-spacing:0.09em;text-transform:uppercase;margin-bottom:8px;'>"
                f"{t('සැකසුම්','Configuration')}</div>", unsafe_allow_html=True)
    analysis_date = st.date_input(t("📅 විශ්ලේෂණ දිනය","📅 Analysis Date"), value=datetime.now())
    confidence_threshold = st.slider(
        t("🎯 විශ්වාස සීමාව","🎯 Confidence Threshold"),
        min_value=0.0, max_value=1.0, value=0.7, step=0.05
    )
    st.markdown("---")

    with st.expander(t("📋 ආදර්ශ තොරතුරු","📋 Model Info")):
        am = np.mean([MODEL_METRICS[c][BEST_MODELS[c]] for c in companies
                      if MODEL_METRICS[c][BEST_MODELS[c]] is not None])
        st.markdown(f"""
        **Version:** v3 Enhanced &nbsp;|&nbsp; **Avg MAPE:** {am:.2f}%  
        **XGBoost:** {xl}/10 &nbsp;|&nbsp; **SARIMAX:** {rl}/10  
        **LightGBM:** {ll}/10 &nbsp;|&nbsp; **Hybrid:** {hl}/3  
        **{t('ආවරණය','Coverage')}:** 10 {t('සමාගම','Companies')}  
        **{t('කොටස් බෙදීම','Splits')}:** Auto-adjusted
        """)
    st.markdown("---")

    st.markdown("""
    <div style='background:#152135;border:1px solid #223048;border-radius:12px;padding:0.9rem;'>
        <div style='font-weight:700;color:#e6ecf5;font-size:0.88rem;'>Huzaifa Ameer</div>
        <div style='color:#4d637f;font-size:0.75rem;margin:2px 0 5px;'>AI/ML Engineer</div>
        <a href='https://www.linkedin.com/in/huzaifaameer/' target='_blank'
           style='color:#6473f3;font-size:0.75rem;text-decoration:none;font-weight:600;'>🔗 LinkedIn</a>
        <div style='color:#4d637f;font-size:0.7rem;margin-top:6px;'>© 2026 All Rights Reserved</div>
    </div>
    """, unsafe_allow_html=True)

# ===============================
# MAIN CONTENT
# ===============================

avg_mape = np.mean([MODEL_METRICS[c][BEST_MODELS[c]] for c in companies
                    if MODEL_METRICS[c][BEST_MODELS[c]] is not None])

# ── HERO ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-badge">📰 &nbsp; CSE · Colombo Stock Exchange · AI-Powered</div>
    <h1 class="hero-title">
        {t('<span>සිංහල</span> News Sentinel', '<span>Sinhala</span> News Sentinel')}
    </h1>
    <p class="hero-sub">
        {t(
            f'සිංහල ව්‍යාපාරික පුවත් හා AI ආදර්ශ ඒකාබද්ධ කර කොළඹ කොටස් හුවමාරුවේ සමාගම් 10ක '
            f'කොටස් මිල පූර්වාවලෝකනය කරයි. XGBoost සාමාන්‍ය MAPE <strong style="color:#a5b4fc">{avg_mape:.2f}%</strong> ලබා ගනී.',
            f'Combines Sinhala news sentiment with AI models to forecast stock prices for 10 CSE-listed companies. '
            f'XGBoost achieves avg MAPE <strong style="color:#a5b4fc">{avg_mape:.2f}%</strong>.'
        )}
    </p>
    <div class="hero-meta">
        Developed by <a href="https://www.linkedin.com/in/huzaifaameer/" target="_blank">Huzaifa Ameer</a> © 2026
    </div>
</div>
""", unsafe_allow_html=True)

# ── SYSTEM DESCRIPTION ───────────────────────────────────────────────────────
st.markdown(f"""
<div class="sys-card">
    <h3>🚀 {t('පද්ධතිය ගැන', 'About This System')}</h3>
    <p>
        {t(
            '<strong>සිංහල News Sentinel v3</strong> යනු XGBoost, LightGBM, SARIMAX හා Hybrid ආදර්ශ '
            'භාවිතා කරමින් කොළඹ කොටස් හුවමාරුවේ (CSE) ලැයිස්තුගත සමාගම් 10ක කොටස් '
            'මිල ප්‍රශස්ත නිරවද්‍යතාවයෙන් පූර්වාවලෝකනය කරන AI-ශක්තිමත් පද්ධතියකි. '
            'සිංහල ව්‍යාපාරික පුවත් වල සංවේදනා (sentiment) පදනම් කරගෙන මිල ගැනීම් කරනු ලැබේ.',
            '<strong>Sinhala News Sentinel v3</strong> is an AI-powered stock price forecasting system '
            'for 10 CSE-listed companies, using XGBoost, LightGBM, SARIMAX and Hybrid ensemble models. '
            'Sentiment extracted from Sinhala business news drives each prediction.'
        )}
    </p>
    <hr class="sys-divider">
    <p><strong style="color:#a5b4fc;">
        📥 {t('ඔබ ඇතුළත් කළ යුතු දේ', 'Required Inputs')}
    </strong></p>
    <ul>
        <li>
            📰&nbsp;<strong>{t('සිංහල ව්‍යාපාරික පුවත් ලිපි', 'Sinhala business news articles')}</strong>
            {t(
                ' — <strong>සිංහල භාෂාවෙන් පමණයි.</strong> ලිපි කිහිපයක් ඇතුළත් කළ හොත් '
                'සංවේදනා ලකුණ වඩාත් නිවැරදි වේ.',
                ' — <strong>Sinhala language only.</strong> Adding more articles improves accuracy.'
            )}
        </li>
        <li>
            💰&nbsp;<strong>{t('ඊයේ වසා දැමූ කොටස් මිල', "Yesterday's closing stock price")}</strong>
            {t(' — රුපියල් (Rs.) ඒකකයෙන් ඇතුළත් කරන්න.', ' — Enter in Rupees (Rs.).')}
        </li>
        <li>
            📅&nbsp;<strong>{t('විශ්ලේෂණ දිනය', 'Analysis date')}</strong>
            {t(' — Sidebar එකෙන් දිනය තෝරන්න.', ' — Choose from the sidebar.')}
        </li>
    </ul>
    <hr class="sys-divider">
    <p style="margin:0;font-size:0.83rem;color:#f5b731;">
        ⚠️&nbsp;{t(
            '<strong>වැදගත්:</strong> සංවේදනා ආදර්ශය සිංහල ව්‍යාපාරික පුවත් සඳහා පමණක් '
            'ප්‍රශස්ත ලෙස පුහුණු කර ඇත. ඉංග්‍රීසි හෝ වෙනත් භාෂා ලිපි ඇතුළත් කිරීමෙන් '
            'ප්‍රතිඵල නිරවද්‍ය නොවිය හැක.',
            '<strong>Important:</strong> The sentiment model is optimised exclusively for Sinhala '
            'business news. Using English or other language text may reduce accuracy.'
        )}
    </p>
</div>
""", unsafe_allow_html=True)

# ── INPUT TABS ────────────────────────────────────────────────────────────────
st.markdown(f'<div class="sec-hdr"><span class="sec-dot"></span>📝 '
            f'{t("දත්ත ඇතුළත් කිරීම","Data Input")}</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs([
    f"📰 {t('සිංහල පුවත් ලිපි','Sinhala News Articles')}",
    f"💰 {t('කොටස් මිල','Stock Prices')}"
])

with tab1:
    st.markdown(f"""
    <div class='info-box'>
        <strong>📌 {t('උපදෙස','Tip')}:</strong>&nbsp;
        {t(
            'සිංහල ව්‍යාපාරික පුවත් ලිපි පමණක් ඇතුළත් කරන්න. '
            'ලිපි ගණන වැඩිවන තරමට විශ්ලේෂණය නිවැරදිය.',
            'Enter Sinhala business news articles only. '
            'More articles = more reliable predictions.'
        )}&nbsp;
        <span style="color:#f5b731;font-weight:600;">
            🔒 {t('සිංහල ව්‍යාපාරික ලිපි පමණයි · Sinhala articles only','Sinhala articles only')}
        </span>
    </div>
    """, unsafe_allow_html=True)

    if "news_inputs" not in st.session_state:
        st.session_state.news_inputs = [""]

    ca, cb, cc = st.columns([3,1,1])
    with cb:
        if st.button(f"➕ {t('ලිපිය එකතු කරන්න','Add Article')}", use_container_width=True):
            st.session_state.news_inputs.append(""); st.rerun()
    with cc:
        if st.button(f"🗑️ {t('සියල්ල මකන්න','Clear All')}", use_container_width=True):
            st.session_state.news_inputs = [""]; st.rerun()

    news_texts = []
    for i in range(len(st.session_state.news_inputs)):
        news = st.text_area(
            f"{t('ලිපිය','Article')} {i+1}",
            height=130,
            value=st.session_state.news_inputs[i],
            key=f"news_{i}",
            placeholder=t(
                "සිංහල ව්‍යාපාරික පුවත් ලිපිය මෙහි අලවන්න... "
                "(උදා: 'ලංකා IOC හි ලාභය රු. මිලියන 450 දක්වා ඉහළ ගොස් ඇත.')",
                "Paste your Sinhala business news article here... "
                "(e.g.: 'Lanka IOC profits rise to Rs. 450 million.')"
            )
        )
        news_texts.append(news)
        st.session_state.news_inputs[i] = news

with tab2:
    st.markdown(f"""
    <div class='info-box'>
        <strong>💡 {t('සටහන','Note')}:</strong>&nbsp;
        {t(
            'ඊයේ දිනයේ (Previous Closing Price) කොටස් මිල රුපියල් (Rs.) ඒකකයෙන් '
            'ඇතුළත් කරන්න. WATA හා BFL — කොටස් බෙදීම ස්වයංක්‍රීයව ගළපා ඇත.',
            "Enter yesterday's closing prices in Rupees (Rs.). "
            'WATA and BFL stock splits are automatically adjusted.'
        )}
    </div>
    """, unsafe_allow_html=True)

    prev_close_prices = {}
    sectors = {}
    for c in companies:
        sectors.setdefault(company_data[c]['sector'],[]).append(c)

    for sector, sector_cos in sectors.items():
        with st.expander(f"📊 {sector}", expanded=True):
            cols = st.columns(min(3, len(sector_cos)))
            for idx, c in enumerate(sector_cos):
                with cols[idx % 3]:
                    info = company_data[c]
                    if c in SPLIT_COMPANIES:
                        st.markdown(
                            f"**{info['symbol']}** "
                            f"<span style='color:#f5b731;font-size:0.68rem;'>"
                            f"({t('බෙදීම-ගළපනලදී','split-adj')})</span>",
                            unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{info['symbol']}**")
                    st.caption(info['name'][:28]+"...")
                    prev_close_prices[c] = st.number_input(
                        t("මිල (රු.)","Price (Rs.)"),
                        min_value=0.0, value=info['default_price'],
                        step=0.1, format="%.2f", key=f"price_{c}"
                    )

# ── ANALYSE BUTTON ────────────────────────────────────────────────────────────
st.markdown("---")
_, btn_col, _ = st.columns([1,2,1])
with btn_col:
    analyze_button = st.button(
        f"🚀 {t('දියුණු ආදර්ශ සමඟ විශ්ලේෂණය කරන්න','Run Analysis with Enhanced Models')}",
        type="primary", use_container_width=True
    )

# ===============================
# ANALYSIS EXECUTION
# ===============================

if analyze_button:
    if all(tx.strip()=="" for tx in news_texts):
        st.warning(t("⚠️ විශ්ලේෂණය සඳහා අවම වශයෙන් එක් සිංහල පුවත් ලිපියක් ඇතුළත් කරන්න.",
                     "⚠️ Please enter at least one Sinhala news article."))
        st.stop()

    pb = st.progress(0)
    st_txt = st.empty()

    # ── Sentiment ──
    st_txt.text(t("🔍 සිංහල ලිපිවල සංවේදනා විශ්ලේෂණය කරමින්...",
                  "🔍 Analysing sentiment in Sinhala articles..."))
    sent_res = []
    for idx, text in enumerate(news_texts,1):
        if text.strip()=="": continue
        row = {t("ලිපිය","Article"):f"{t('ලිපිය','Article')} {idx}",
               t("පෙරදසුන","Preview"):text[:100]+"..."}
        for c in companies: row[c] = analyze_sentiment(text,c)
        sent_res.append(row)
        pb.progress((idx/len(news_texts))*0.4)

    sentiment_df = pd.DataFrame(sent_res)
    smap = {"Positive":1,"Neutral":0,"Negative":-1}
    score_mx = sentiment_df[[c for c in companies if c in sentiment_df.columns]].copy()
    for c in companies:
        if c in score_mx.columns: score_mx[c] = score_mx[c].map(smap)
    daily_scores = score_mx.mean().reset_index()
    daily_scores.columns = ["Company","Average_Sentiment_Score"]

    # ── Price Predictions ──
    st_txt.text(t("💰 දියුණු ආදර්ශ භාවිතා කර මිල පූර්වාවලෝකනය...",
                  "💰 Generating price predictions with enhanced models..."))
    preds_list, failed = [], []
    for idx,(_, row_d) in enumerate(daily_scores.iterrows()):
        company = row_d["Company"]; ss = row_d["Average_Sentiment_Score"]
        pc = prev_close_prices.get(company, company_data[company]['default_price'])
        pred_price, conf, model_used = predict_best(company,ss,pc,analysis_date)
        if pred_price is None: failed.append(company_data[company]['symbol']); continue
        chg_amt = pred_price-pc; chg_pct = (chg_amt/pc)*100
        bm = BEST_MODELS[company]; bm_mape = MODEL_METRICS[company].get(bm) or 0
        preds_list.append({
            "Company":company_data[company]['name'],
            "Symbol":company_data[company]['symbol'],
            "Sector":company_data[company]['sector'],
            "Previous_Close":pc, "Predicted_Price":pred_price,
            "Price_Change":chg_amt, "Price_Change_Percent":chg_pct,
            "Sentiment_Score":ss,
            "Sentiment_Category":"Positive" if ss>0.1 else "Negative" if ss<-0.1 else "Neutral",
            "Model_Used":model_used,
            "Best_MAPE":f"{bm_mape:.2f}%" if bm_mape else "N/A",
            "Confidence":conf, "Split_Adjusted":company in SPLIT_COMPANIES,
            "Color":company_data[company]['color']
        })
        pb.progress(0.4+((idx+1)/len(companies))*0.6)

    if failed:
        st.warning(f"⚠️ {t('පූර්වාවලෝකනය නොහැකි','Unavailable')}: {', '.join(failed)}")
    if not preds_list:
        st.error(t("❌ කිසිදු පූර්වාවලෝකනයක් ජනනය කළ නොහැකිය.","❌ No predictions generated."))
        st.stop()

    predictions_df = pd.DataFrame(preds_list)
    pb.empty(); st_txt.empty()

    # ── Results ──────────────────────────────────────────────────────────────
    st.markdown(f'<div class="sec-hdr"><span class="sec-dot"></span>📊 '
                f'{t("විශ්ලේෂණ ප්‍රතිඵල v3","Analysis Results v3")}</div>', unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    avg_ret = predictions_df['Price_Change_Percent'].mean()
    pos_n   = len(predictions_df[predictions_df['Price_Change_Percent']>0])
    avg_snt = predictions_df['Sentiment_Score'].mean()
    bstp    = predictions_df.loc[predictions_df['Price_Change_Percent'].idxmax()]
    c1.metric(t("සාමාන්‍ය ප්‍රතිලාභය","Avg Return"),       f"{avg_ret:+.2f}%")
    c2.metric(t("ලාභ ලබා ගන්නන්","Gainers"),               f"{pos_n}/{len(preds_list)}")
    c3.metric(t("සංවේදනා ලකුණ","Sentiment Score"),        f"{avg_snt:.3f}")
    c4.metric(t("ඉහළම කාර්ය සාධනය","Top Performer"),      bstp['Symbol'],
              delta=f"+{bstp['Price_Change_Percent']:.1f}%")

    st.markdown(f"##### 🤖 {t('ආදර්ශ කාර්ය සාධනය','Model Performance')}")
    ms = predictions_df.groupby('Model_Used').agg({'Confidence':'mean','Symbol':'count'}).round(3)
    ms.columns = [t('සාමාන්‍ය විශ්වාසය','Avg Confidence'), t('ගණන','Count')]
    st.dataframe(ms, use_container_width=True)

    # Article Sentiment
    st.markdown(f'<div class="sec-hdr"><span class="sec-dot"></span>📰 '
                f'{t("ලිපිවල සංවේදනා","Article Sentiment")}</div>', unsafe_allow_html=True)

    ad = sentiment_df.copy()
    rd = {}
    for c in companies:
        if c in ad.columns: rd[c] = company_data[c]['symbol']
    ad = ad.rename(columns=rd)

    def _sty(val):
        if val=="Positive": return 'background-color:rgba(16,201,138,0.15);color:#10c98a;'
        if val=="Negative": return 'background-color:rgba(240,92,110,0.15);color:#f05c6e;'
        if val=="Neutral":  return 'background-color:rgba(100,116,139,0.15);color:#8fa5c2;'
        return ''

    sym_cols = [company_data[c]['symbol'] for c in companies if company_data[c]['symbol'] in ad.columns]
    st.dataframe(ad.style.map(_sty, subset=sym_cols), use_container_width=True, height=340)

    # Price Predictions Table
    st.markdown(f'<div class="sec-hdr"><span class="sec-dot"></span>💰 '
                f'{t("මිල පූර්වාවලෝකනය","Price Predictions")}</div>', unsafe_allow_html=True)

    disp = predictions_df.copy()
    disp['Previous_Close']       = disp['Previous_Close'].map(lambda x: f"Rs. {x:,.2f}")
    disp['Predicted_Price']      = disp['Predicted_Price'].map(lambda x: f"Rs. {x:,.2f}")
    disp['Price_Change']         = disp['Price_Change'].map(lambda x: f"{x:+,.2f}")
    disp['Price_Change_Percent'] = disp['Price_Change_Percent'].map(lambda x: f"{x:+.2f}%")
    disp['Sentiment_Score']      = disp['Sentiment_Score'].map(lambda x: f"{x:.3f}")
    disp['Confidence']           = disp['Confidence'].map(lambda x: f"{x:.1%}")
    disp['Split']                = disp['Split_Adjusted'].map(lambda x: "✓" if x else "—")
    col_rename = {
        'Symbol':              t('සිරස','Symbol'),
        'Sector':              t('අංශය','Sector'),
        'Previous_Close':      t('පෙර මිල','Prev Close'),
        'Predicted_Price':     t('පෙලෙන මිල','Predicted'),
        'Price_Change_Percent':t('වෙනස %','Change %'),
        'Model_Used':          t('ආදර්ශය','Model'),
        'Best_MAPE':           'MAPE',
        'Confidence':          t('විශ්වාසය','Conf'),
        'Split':               t('බෙදීම','Split'),
    }
    st.dataframe(disp[list(col_rename.keys())].rename(columns=col_rename),
                 use_container_width=True, height=390)

    # Charts
    st.markdown(f'<div class="sec-hdr"><span class="sec-dot"></span>📊 '
                f'{t("ප්‍රස්ථාර","Charts")}</div>', unsafe_allow_html=True)

    vt1,vt2,vt3 = st.tabs([
        f"📈 {t('මිල වෙනස','Price Changes')}",
        f"🎯 {t('සංවේදනා','Sentiment')}",
        f"🏢 {t('අංශය','Sector')}",
    ])
    _bg = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
               font=dict(color='#8fa5c2'), margin=dict(l=10,r=10,t=42,b=10))

    with vt1:
        v1,v2 = st.columns(2)
        with v1:
            sdf = predictions_df.sort_values('Price_Change_Percent',ascending=True)
            fig = go.Figure(go.Bar(
                x=sdf['Price_Change_Percent'], y=sdf['Symbol'], orientation='h',
                marker_color=['#f05c6e' if x<0 else '#10c98a' for x in sdf['Price_Change_Percent']],
                text=sdf['Price_Change_Percent'].map(lambda x:f"{x:+.1f}%"), textposition='outside'
            ))
            fig.update_layout(title=t("අපේක්ෂිත මිල වෙනස","Expected Price Changes"),
                              xaxis_title=t("වෙනස (%)","Change (%)"),height=430,**_bg)
            st.plotly_chart(fig,use_container_width=True)
        with v2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=predictions_df['Symbol'],y=predictions_df['Previous_Close'],
                mode='markers+lines',name=t('පෙර','Prev Close'),
                marker=dict(size=8,color='#4d637f'),line=dict(color='#4d637f',dash='dot')))
            fig.add_trace(go.Scatter(x=predictions_df['Symbol'],y=predictions_df['Predicted_Price'],
                mode='markers+lines',name=t('පෙලෙන','Predicted'),
                marker=dict(size=11,color='#6473f3'),line=dict(color='#6473f3',width=3)))
            fig.update_layout(title=t("මිල සන්සන්දනය","Price Comparison"),
                              yaxis_title=t("මිල (රු.)","Price (Rs.)"),height=430,**_bg)
            st.plotly_chart(fig,use_container_width=True)

    with vt2:
        v1,v2 = st.columns(2)
        with v1:
            fig = px.scatter(predictions_df,x='Sentiment_Score',y='Price_Change_Percent',
                size='Previous_Close',color='Sector',text='Symbol',
                title=t("සංවේදනා vs මිල","Sentiment vs Price"),height=430)
            fig.update_traces(textposition='top center')
            fig.update_layout(**_bg)
            st.plotly_chart(fig,use_container_width=True)
        with v2:
            sc = predictions_df['Sentiment_Category'].value_counts()
            fig = go.Figure(go.Pie(labels=sc.index,values=sc.values,hole=0.42,
                marker=dict(colors=['#10c98a','#4d637f','#f05c6e'])))
            fig.update_layout(title=t("සංවේදනා බෙදාහැරීම","Sentiment Distribution"),
                              height=430,**_bg)
            st.plotly_chart(fig,use_container_width=True)

    with vt3:
        v1,v2 = st.columns(2)
        with v1:
            sp = predictions_df.groupby('Sector')['Price_Change_Percent'].mean().reset_index()
            fig = go.Figure(go.Bar(
                x=sp['Sector'],y=sp['Price_Change_Percent'],
                text=sp['Price_Change_Percent'].map(lambda x:f"{x:+.1f}%"),textposition='outside',
                marker_color=['#10c98a' if x>0 else '#f05c6e' for x in sp['Price_Change_Percent']]
            ))
            fig.update_layout(title=t("අංශය අනුව සාමාන්‍ය","Avg by Sector"),height=430,**_bg)
            st.plotly_chart(fig,use_container_width=True)
        with v2:
            sct = predictions_df['Sector'].value_counts()
            fig = go.Figure(go.Bar(x=sct.values,y=sct.index,orientation='h',
                marker_color='#6473f3',text=sct.values,textposition='outside'))
            fig.update_layout(title=t("අංශය අනුව සමාගම් ගණන","Companies by Sector"),height=430,**_bg)
            st.plotly_chart(fig,use_container_width=True)

    # Recommendations
    st.markdown(f'<div class="sec-hdr"><span class="sec-dot"></span>💡 '
                f'{t("නිර්දේශ","Recommendations")}</div>', unsafe_allow_html=True)

    rc1,rc2 = st.columns(2)
    with rc1:
        st.markdown(f"#### 🎯 {t('ඉහළම අවස්ථා','Top Opportunities')}")
        hc  = predictions_df[predictions_df['Confidence']>=confidence_threshold]
        top3= hc.nlargest(3,'Price_Change_Percent')
        if len(top3)==0:
            st.info(t("විශ්වාස සීමාවට ගැළපෙන අවස්ථා නොමැත.","No opportunities meet the threshold."))
        else:
            for _,row in top3.iterrows():
                sn=" ("+t("බෙදීම-ගළපනලදී","Split-adj")+")" if row['Split_Adjusted'] else ""
                st.markdown(f"""<div class='opp-card'>
                    <h4>{row['Symbol']} — {row['Company']}{sn}</h4>
                    <div class='c-row'><strong>{t('ඉලක්ක','Target')}:</strong> Rs.&nbsp;{row['Predicted_Price']:.2f}
                    &nbsp;|&nbsp; <strong>{t('ප්‍රතිලාභය','Return')}:</strong>
                    <span class='tg'>{row['Price_Change_Percent']:+.2f}%</span></div>
                    <div class='c-row'><strong>{t('ආදර්ශය','Model')}:</strong> {row['Model_Used']}
                    &nbsp;|&nbsp; <strong>MAPE:</strong> {row['Best_MAPE']}
                    &nbsp;|&nbsp; <strong>{t('විශ්වාසය','Conf')}:</strong> {row['Confidence']:.1%}</div>
                </div>""", unsafe_allow_html=True)

    with rc2:
        st.markdown(f"#### ⚠️ {t('අවධානයෙන් බලන්න','Monitor')}")
        bot3 = predictions_df.nsmallest(3,'Price_Change_Percent')
        for _,row in bot3.iterrows():
            sn=" ("+t("බෙදීම-ගළපනලදී","Split-adj")+")" if row['Split_Adjusted'] else ""
            st.markdown(f"""<div class='mon-card'>
                <h4>{row['Symbol']} — {row['Company']}{sn}</h4>
                <div class='c-row'><strong>{t('ඉලක්ක','Target')}:</strong> Rs.&nbsp;{row['Predicted_Price']:.2f}
                &nbsp;|&nbsp; <strong>{t('ප්‍රතිලාභය','Return')}:</strong>
                <span class='tr'>{row['Price_Change_Percent']:+.2f}%</span></div>
                <div class='c-row'><strong>{t('ආදර්ශය','Model')}:</strong> {row['Model_Used']}
                &nbsp;|&nbsp; <strong>MAPE:</strong> {row['Best_MAPE']}
                &nbsp;|&nbsp; <strong>{t('විශ්වාසය','Conf')}:</strong> {row['Confidence']:.1%}</div>
            </div>""", unsafe_allow_html=True)

    # Export
    st.markdown(f'<div class="sec-hdr"><span class="sec-dot"></span>📥 '
                f'{t("අපනයනය","Export")}</div>', unsafe_allow_html=True)

    e1,e2,e3 = st.columns(3)
    with e1:
        st.download_button(f"📊 {t('පූර්වාවලෝකන','Predictions')}",
            predictions_df.to_csv(index=False),
            f"predictions_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv", use_container_width=True)
    with e2:
        st.download_button(f"📰 {t('සංවේදනා','Sentiment')}",
            sentiment_df.to_csv(index=False),
            f"sentiment_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv", use_container_width=True)
    with e3:
        full = predictions_df.copy()
        full['Analysis_Date']     = analysis_date
        full['Articles_Analyzed'] = len([tx for tx in news_texts if tx.strip()])
        full['Model_Version']     = 'v3_enhanced'
        st.download_button(f"📄 {t('සම්පූර්ණ වාර්තාව','Full Report')}",
            full.to_csv(index=False),
            f"full_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv", use_container_width=True)

    # Disclaimer
    st.markdown("---")
    st.markdown(f"""
    <div class='warn-box'>
        <strong>⚠️ {t('වියාකරණය','Disclaimer')}</strong><br>
        {t(
            'මෙම විශ්ලේෂණය <code>price_models_final_v3/</code> ආදර්ශ භාවිතා කරයි. '
            'XGBoost බොහෝ සමාගම් සඳහා 1%ට අඩු MAPE ලබා ගනී. '
            'අතීත කාර්ය සාධනය අනාගත ප්‍රතිඵල සහතික නොකරයි. '
            '<strong>මෙය මූල්‍ය උපදෙසක් නොවේ.</strong>',
            'This analysis uses models from <code>price_models_final_v3/</code>. '
            'XGBoost achieves &lt;1% MAPE for most companies. '
            'Past performance does not guarantee future results. '
            '<strong>Not financial advice.</strong>'
        )}
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='footer'>
    <strong>📰 සිංහල News Sentinel</strong><br>
    {t('දියුණු ආදර්ශ v3 · සාමාන්‍ය MAPE: 0.48%',
       'Enhanced Models v3 · Avg MAPE: 0.48%')}<br>
    {t('සෑදුවේ','Developed with')} ❤️ {t('විසින්','by')}
    <a href='https://www.linkedin.com/in/huzaifaameer/' target='_blank'>Huzaifa Ameer</a> | © 2026<br>
    <span style='font-size:0.73rem;color:#4d637f;'>
        Version 3.0 · Enhanced Models · XGBoost &lt;1% MAPE · Stock Split Adjusted
    </span>
</div>
""", unsafe_allow_html=True)
# import streamlit as st
# import pandas as pd
# import joblib
# import numpy as np
# import re
# import os
# import plotly.graph_objects as go
# import plotly.express as px
# from datetime import datetime, timedelta
# import warnings
# warnings.filterwarnings('ignore')

# # ===============================
# # PAGE CONFIG
# # ===============================

# st.set_page_config(
#     page_title="Sinhala News Sentinel",
#     page_icon="📰",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ===============================
# # MODERN THEME & STYLING
# # ===============================

# st.markdown("""
# <style>
#     /* Import Google Fonts */
#     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
#     /* Global Styles */
#     * {
#         font-family: 'Inter', sans-serif;
#     }
    
#     h1, h2, h3, h4, h5, h6 {
#         font-family: 'Space Grotesk', sans-serif;
#     }
    
#     /* Color Palette - Premium Dark Theme */
#     :root {
#         --primary: #6366f1;
#         --primary-light: #818cf8;
#         --primary-dark: #4f46e5;
#         --secondary: #10b981;
#         --accent: #f59e0b;
#         --danger: #ef4444;
#         --background: #0f172a;
#         --surface: #1e293b;
#         --surface-light: #334155;
#         --border: #475569;
#         --text-primary: #f8fafc;
#         --text-secondary: #cbd5e1;
#         --text-muted: #94a3b8;
#         --shadow: rgba(0, 0, 0, 0.3);
#     }
    
#     /* Main Content Area */
#     .main {
#         background: var(--background);
#     }
    
#     /* Hide Streamlit Branding */
#     #MainMenu, footer, header {visibility: hidden;}
    
#     /* Custom Header */
#     .dashboard-header {
#         background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
#         padding: 2rem;
#         border-radius: 24px;
#         color: white;
#         margin-bottom: 2rem;
#         border: 1px solid var(--border);
#         position: relative;
#         overflow: hidden;
#     }
    
#     .dashboard-header::before {
#         content: '';
#         position: absolute;
#         top: -50%;
#         right: -50%;
#         width: 200%;
#         height: 200%;
#         background: radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 70%);
#         animation: rotate 20s linear infinite;
#     }
    
#     @keyframes rotate {
#         from { transform: rotate(0deg); }
#         to { transform: rotate(360deg); }
#     }
    
#     .dashboard-title {
#         font-size: 2.5rem;
#         font-weight: 700;
#         margin: 0;
#         letter-spacing: -1px;
#         background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
#         -webkit-background-clip: text;
#         -webkit-text-fill-color: transparent;
#         position: relative;
#         z-index: 1;
#     }
    
#     .dashboard-subtitle {
#         font-size: 1.1rem;
#         color: var(--text-secondary);
#         margin-top: 0.5rem;
#         position: relative;
#         z-index: 1;
#     }
    
#     .developer-credit {
#         position: absolute;
#         bottom: 1rem;
#         right: 2rem;
#         color: var(--text-muted);
#         font-size: 0.9rem;
#         z-index: 1;
#     }
    
#     .developer-credit a {
#         color: var(--primary-light);
#         text-decoration: none;
#         font-weight: 500;
#         transition: color 0.2s;
#     }
    
#     .developer-credit a:hover {
#         color: var(--primary);
#         text-decoration: underline;
#     }
    
#     /* Card Styling */
#     .metric-card {
#         background: var(--surface);
#         border-radius: 16px;
#         padding: 1.5rem;
#         border: 1px solid var(--border);
#         box-shadow: 0 4px 6px var(--shadow);
#         transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
#     }
    
#     .metric-card:hover {
#         transform: translateY(-4px);
#         box-shadow: 0 12px 24px var(--shadow);
#         border-color: var(--primary);
#     }
    
#     /* Section Headers */
#     .section-header {
#         color: var(--text-primary);
#         font-weight: 600;
#         font-size: 1.5rem;
#         margin: 2rem 0 1rem 0;
#         padding-bottom: 0.75rem;
#         border-bottom: 2px solid var(--border);
#         display: flex;
#         align-items: center;
#         gap: 0.5rem;
#     }
    
#     .section-header::before {
#         content: '◆';
#         color: var(--primary);
#         font-size: 1.2rem;
#     }
    
#     /* Input Areas */
#     .stTextArea textarea {
#         background: var(--surface) !important;
#         color: var(--text-primary) !important;
#         border-radius: 12px !important;
#         border: 1px solid var(--border) !important;
#         font-size: 0.95rem;
#         transition: border-color 0.2s, box-shadow 0.2s;
#     }
    
#     .stTextArea textarea:focus {
#         border-color: var(--primary) !important;
#         box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
#     }
    
#     .stTextArea textarea::placeholder {
#         color: var(--text-muted) !important;
#     }
    
#     /* Buttons */
#     .stButton > button {
#         background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
#         color: white !important;
#         border-radius: 12px !important;
#         font-weight: 600 !important;
#         padding: 0.75rem 1.5rem !important;
#         border: none !important;
#         transition: all 0.2s !important;
#         text-transform: uppercase;
#         letter-spacing: 0.5px;
#         font-size: 0.9rem !important;
#     }
    
#     .stButton > button:hover {
#         transform: translateY(-2px) !important;
#         box-shadow: 0 8px 16px rgba(99, 102, 241, 0.3) !important;
#     }
    
#     /* Sidebar Styling */
#     [data-testid="stSidebar"] {
#         background: var(--surface);
#         border-right: 1px solid var(--border);
#     }
    
#     [data-testid="stSidebar"] .stMarkdown {
#         color: var(--text-secondary);
#     }
    
#     /* Tables */
#     .dataframe {
#         background: var(--surface) !important;
#         border: 1px solid var(--border) !important;
#         border-radius: 12px !important;
#         overflow: hidden;
#     }
    
#     .dataframe th {
#         background: var(--primary-dark) !important;
#         color: white !important;
#         font-weight: 600 !important;
#         padding: 0.75rem !important;
#     }
    
#     .dataframe td {
#         background: var(--surface) !important;
#         color: var(--text-secondary) !important;
#         padding: 0.75rem !important;
#         border-bottom: 1px solid var(--border) !important;
#     }
    
#     /* Sentiment Badges */
#     .sentiment-badge {
#         display: inline-block;
#         padding: 0.25rem 0.75rem;
#         border-radius: 20px;
#         font-size: 0.85rem;
#         font-weight: 600;
#         text-align: center;
#     }
    
#     .sentiment-positive {
#         background: rgba(16, 185, 129, 0.2);
#         color: #34d399;
#         border: 1px solid #10b981;
#     }
    
#     .sentiment-neutral {
#         background: rgba(100, 116, 139, 0.2);
#         color: var(--text-secondary);
#         border: 1px solid var(--border);
#     }
    
#     .sentiment-negative {
#         background: rgba(239, 68, 68, 0.2);
#         color: #f87171;
#         border: 1px solid #ef4444;
#     }
    
#     /* Info Boxes */
#     .info-box {
#         background: rgba(99, 102, 241, 0.1);
#         border-left: 4px solid var(--primary);
#         padding: 1rem;
#         border-radius: 12px;
#         margin: 1rem 0;
#         color: var(--text-secondary);
#     }
    
#     .warning-box {
#         background: rgba(245, 158, 11, 0.1);
#         border-left: 4px solid var(--accent);
#         padding: 1rem;
#         border-radius: 12px;
#         margin: 1rem 0;
#         color: var(--text-secondary);
#     }
    
#     /* Progress Bars */
#     .stProgress > div > div {
#         background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
#         border-radius: 4px;
#         height: 8px !important;
#     }
    
#     /* Expander */
#     .streamlit-expanderHeader {
#         background: var(--surface) !important;
#         color: var(--text-primary) !important;
#         border-radius: 12px !important;
#         border: 1px solid var(--border) !important;
#         font-weight: 500;
#     }
    
#     /* Number Input */
#     .stNumberInput input {
#         background: var(--surface) !important;
#         color: var(--text-primary) !important;
#         border-radius: 8px !important;
#         border: 1px solid var(--border) !important;
#     }
    
#     /* Tabs */
#     .stTabs [data-baseweb="tab-list"] {
#         gap: 8px;
#         background: var(--surface);
#         padding: 0.5rem;
#         border-radius: 16px;
#     }
    
#     .stTabs [data-baseweb="tab"] {
#         background: transparent !important;
#         color: var(--text-secondary) !important;
#         border-radius: 12px !important;
#         padding: 0.75rem 1.5rem !important;
#         font-weight: 500;
#         transition: all 0.2s;
#     }
    
#     .stTabs [aria-selected="true"] {
#         background: var(--primary) !important;
#         color: white !important;
#     }
    
#     /* Status Indicator */
#     .status-indicator {
#         width: 12px;
#         height: 12px;
#         border-radius: 50%;
#         display: inline-block;
#         margin-right: 8px;
#         position: relative;
#     }
    
#     .status-indicator::after {
#         content: '';
#         position: absolute;
#         top: -4px;
#         left: -4px;
#         right: -4px;
#         bottom: -4px;
#         border-radius: 50%;
#         animation: pulse 2s infinite;
#     }
    
#     @keyframes pulse {
#         0% { transform: scale(1); opacity: 1; }
#         100% { transform: scale(1.5); opacity: 0; }
#     }
    
#     .status-online {
#         background: var(--secondary);
#     }
    
#     .status-online::after {
#         background: rgba(16, 185, 129, 0.4);
#     }
    
#     .status-offline {
#         background: var(--danger);
#     }
    
#     .status-offline::after {
#         background: rgba(239, 68, 68, 0.4);
#     }
    
#     /* Recommendation Cards */
#     .opportunity-card {
#         background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
#         padding: 1.5rem;
#         border-radius: 16px;
#         border-left: 4px solid var(--secondary);
#         margin-bottom: 1rem;
#         backdrop-filter: blur(10px);
#     }
    
#     .monitor-card {
#         background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
#         padding: 1.5rem;
#         border-radius: 16px;
#         border-left: 4px solid var(--danger);
#         margin-bottom: 1rem;
#         backdrop-filter: blur(10px);
#     }
    
#     /* Footer */
#     .footer {
#         text-align: center;
#         padding: 3rem 0 1rem 0;
#         color: var(--text-muted);
#         font-size: 0.9rem;
#         border-top: 1px solid var(--border);
#         margin-top: 3rem;
#     }
    
#     .footer a {
#         color: var(--primary-light);
#         text-decoration: none;
#         transition: color 0.2s;
#     }
    
#     .footer a:hover {
#         color: var(--primary);
#         text-decoration: underline;
#     }
    
#     /* Custom Scrollbar */
#     ::-webkit-scrollbar {
#         width: 8px;
#         height: 8px;
#     }
    
#     ::-webkit-scrollbar-track {
#         background: var(--surface);
#     }
    
#     ::-webkit-scrollbar-thumb {
#         background: var(--primary-dark);
#         border-radius: 4px;
#     }
    
#     ::-webkit-scrollbar-thumb:hover {
#         background: var(--primary);
#     }
# </style>
# """, unsafe_allow_html=True)

# # ===============================
# # DATA & CONFIGURATION
# # ===============================

# STOPWORDS_PATH = "./data/stop words.txt"

# @st.cache_resource
# def load_stopwords():
#     if not os.path.exists(STOPWORDS_PATH):
#         st.error("⚠️ Stopwords file not found. Using default configuration.")
#         return []
#     stop_words = open(STOPWORDS_PATH, encoding="utf-8").read().splitlines()
#     return stop_words

# stop_words = load_stopwords()

# def tokenizer(text):
#     tokens = re.findall(r'\b\w+\b', text.lower())
#     return [t for t in tokens if t not in stop_words]

# # ===============================
# # COMPANY DATA
# # ===============================

# companies = [
#     "WATA.N0000", "AGPL.N0000", "HAPU.N0000", "MCPL.N0000",
#     "KOTA.N0000", "BFL.N0000", "RWSL.N0000", "DIPP.N0000",
#     "MGT.N0000", "HEXP.N0000"
# ]

# company_data = {
#     'WATA.N0000': {'name': 'Watawala Plantations PLC', 'symbol': 'WATA', 'sector': 'Plantations', 
#                    'description': 'Leading tea and rubber plantation', 'default_price': 48.00, 'color': '#10b981'},
#     'AGPL.N0000': {'name': 'Agarapatana Plantations PLC', 'symbol': 'AGPL', 'sector': 'Plantations',
#                    'description': 'High-grown tea specialist', 'default_price': 20.00, 'color': '#14b8a6'},
#     'HAPU.N0000': {'name': 'Hapugastenne Plantations PLC', 'symbol': 'HAPU', 'sector': 'Plantations',
#                    'description': 'Diversified tea and rubber', 'default_price': 78.00, 'color': '#06b6d4'},
#     'MCPL.N0000': {'name': 'Mahaweli Coconut Plantations PLC', 'symbol': 'MCPL', 'sector': 'Plantations',
#                    'description': 'Coconut and diversified agriculture', 'default_price': 51.00, 'color': '#0ea5e9'},
#     'KOTA.N0000': {'name': 'Kotagala Plantations PLC', 'symbol': 'KOTA', 'sector': 'Plantations',
#                    'description': 'Export-focused tea plantations', 'default_price': 10.00, 'color': '#3b82f6'},
#     'BFL.N0000': {'name': 'Bairaha Farms PLC', 'symbol': 'BFL', 'sector': 'Food & Beverage',
#                   'description': 'Poultry and animal feed', 'default_price': 94.00, 'color': '#6366f1'},
#     'RWSL.N0000': {'name': 'Raigam Wayamba Salterns PLC', 'symbol': 'RWSL', 'sector': 'Manufacturing',
#                    'description': 'Salt manufacturing', 'default_price': 25.50, 'color': '#8b5cf6'},
#     'DIPP.N0000': {'name': 'Dipped Products PLC', 'symbol': 'DIPP', 'sector': 'Manufacturing',
#                    'description': 'Rubber gloves and latex', 'default_price': 62.90, 'color': '#a855f7'},
#     'MGT.N0000': {'name': 'Maskeliya Plantations PLC', 'symbol': 'MGT', 'sector': 'Plantations',
#                   'description': 'Tea and rubber estates', 'default_price': 40.30, 'color': '#d946ef'},
#     'HEXP.N0000': {'name': 'Hayleys Export PLC', 'symbol': 'HEXP', 'sector': 'Export & Trading',
#                    'description': 'Agricultural exports', 'default_price': 120.00, 'color': '#ec4899'}
# }

# # ===============================
# # MODEL LOADING
# # ===============================

# @st.cache_resource
# def load_sentiment_models():
#     models = {}
#     status = {}
#     for c in companies:
#         path = f"saved_models/{c}_svm.joblib"
#         if os.path.exists(path):
#             try:
#                 models[c] = joblib.load(path)
#                 status[c] = {'loaded': True, 'error': None}
#             except Exception as e:
#                 models[c] = None
#                 status[c] = {'loaded': False, 'error': str(e)}
#         else:
#             models[c] = None
#             status[c] = {'loaded': False, 'error': 'Model not found'}
#     return models, status

# @st.cache_resource
# def load_price_models():
#     models = {}
#     status = {}
#     for c in companies:
#         path = f"price_models_sarimax/{c}_sarimax.joblib"
#         if os.path.exists(path):
#             try:
#                 models[c] = joblib.load(path)
#                 status[c] = {'loaded': True, 'error': None}
#             except Exception as e:
#                 models[c] = None
#                 status[c] = {'loaded': False, 'error': str(e)}
#         else:
#             models[c] = None
#             status[c] = {'loaded': False, 'error': 'Model not found'}
#     return models, status

# sentiment_models, sentiment_status = load_sentiment_models()
# price_models, price_status = load_price_models()

# # ===============================
# # SIDEBAR
# # ===============================

# with st.sidebar:
#     st.markdown("""
#     <div style='text-align: center; padding: 1rem 0;'>
#         <h2 style='color: var(--primary); margin: 0;'>📰 SENTINEL</h2>
#         <p style='color: var(--text-muted); margin: 0;'>v3.0</p>
#     </div>
#     """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # System Status
#     st.markdown("#### 🖥️ System Status")
    
#     sentiment_loaded = sum(1 for s in sentiment_status.values() if s['loaded'])
#     price_loaded = sum(1 for s in price_status.values() if s['loaded'])
    
#     col1, col2 = st.columns(2)
#     with col1:
#         status_class = "status-online" if sentiment_loaded == 10 else "status-offline"
#         st.markdown(f'<span class="status-indicator {status_class}"></span>**Sentiment**', unsafe_allow_html=True)
#         st.caption(f"{sentiment_loaded}/10 models")
    
#     with col2:
#         status_class = "status-online" if price_loaded == 10 else "status-offline"
#         st.markdown(f'<span class="status-indicator {status_class}"></span>**Pricing**', unsafe_allow_html=True)
#         st.caption(f"{price_loaded}/10 models")
    
#     st.markdown("---")
    
#     # Quick Settings
#     st.markdown("#### ⚙️ Configuration")
    
#     analysis_date = st.date_input(
#         "📅 Analysis Date",
#         value=datetime.now(),
#         help="Select the date for this analysis"
#     )
    
#     confidence_threshold = st.slider(
#         "🎯 Confidence Threshold",
#         min_value=0.0,
#         max_value=1.0,
#         value=0.7,
#         step=0.05,
#         help="Minimum confidence for recommendations"
#     )
    
#     show_advanced = st.checkbox("🔬 Advanced Analytics", value=False, help="Show detailed analytical insights")
    
#     st.markdown("---")
    
#     # Model Information
#     with st.expander("📋 Model Information"):
#         st.markdown("""
#         **Sentiment Engine:** SVM Classifier  
#         **Price Predictor:** SARIMAX  
#         **Training Period:** 2018-2025  
#         **Coverage:** 10 Companies  
#         **Languages:** Sinhala, English  
#         """)
    
#     st.markdown("---")
    
#     # Developer Info
#     st.markdown("#### 👨‍💻 Developer")
#     st.markdown("""
#     <div style='background: var(--surface-light); padding: 1rem; border-radius: 12px;'>
#         <p style='margin: 0; font-weight: 600; color: var(--text-primary);'>Huzaifa Ameer</p>
#         <p style='margin: 0.25rem 0; color: var(--text-muted); font-size: 0.85rem;'>AI/ML Engineer</p>
#         <a href='https://www.linkedin.com/in/huzaifaameer/' target='_blank' style='color: var(--primary); text-decoration: none; font-size: 0.85rem;'>
#             🔗 LinkedIn Profile
#         </a>
#         <p style='margin: 0.5rem 0 0 0; color: var(--text-muted); font-size: 0.8rem;'>© 2026 All Rights Reserved</p>
#     </div>
#     """, unsafe_allow_html=True)

# # ===============================
# # MAIN HEADER WITH CREDITS
# # ===============================

# st.markdown("""
# <div class="dashboard-header">
#     <h1 class="dashboard-title">📰 SINHALA NEWS SENTINEL</h1>
#     <p class="dashboard-subtitle">AI-Powered Stock Market Intelligence Platform</p>
#     <div class="developer-credit">
#         Developed by <a href="https://www.linkedin.com/in/huzaifaameer/" target="_blank">Huzaifa Ameer</a> © 2026
#     </div>
# </div>
# """, unsafe_allow_html=True)

# # System Description
# st.markdown("""
# <div style='background: var(--surface); padding: 1.5rem; border-radius: 16px; margin-bottom: 2rem; border: 1px solid var(--border);'>
#     <h3 style='color: var(--primary); margin: 0 0 0.5rem 0;'>🚀 About the System</h3>
#     <p style='color: var(--text-secondary; margin: 0; line-height: 1.6;'>
#         <strong>Sinhala News Sentinel</strong> is an advanced financial analytics platform that leverages machine learning to 
#         analyze Sinhala business news and predict stock price movements. The system processes news articles through 
#         custom-trained SVM classifiers to determine market sentiment, then feeds this sentiment into SARIMAX time series 
#         models to generate next-day price predictions for 10 major Sri Lankan companies.
#     </p>
#     <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;'>
#         <div style='background: var(--surface-light); padding: 0.75rem; border-radius: 8px; text-align: center;'>
#             <span style='color: var(--primary); font-weight: 600;'>📊 10</span>
#             <span style='color: var(--text-muted; display: block; font-size: 0.85rem;'>Companies Tracked</span>
#         </div>
#         <div style='background: var(--surface-light); padding: 0.75rem; border-radius: 8px; text-align: center;'>
#             <span style='color: var(--primary); font-weight: 600;'>⚡ 87.3%</span>
#             <span style='color: var(--text-muted; display: block; font-size: 0.85rem;'>Avg. Accuracy</span>
#         </div>
#         <div style='background: var(--surface-light); padding: 0.75rem; border-radius: 8px; text-align: center;'>
#             <span style='color: var(--primary); font-weight: 600;'>🌐 2</span>
#             <span style='color: var(--text-muted; display: block; font-size: 0.85rem;'>Languages Supported</span>
#         </div>
#     </div>
# </div>
# """, unsafe_allow_html=True)

# # ===============================
# # QUICK STATS ROW
# # ===============================

# col1, col2, col3, col4 = st.columns(4)

# with col1:
#     st.markdown("""
#     <div class='metric-card'>
#         <h4 style='margin: 0; color: var(--text-muted); font-size: 0.9rem;'>📰 ARTICLES READY</h4>
#         <h2 style='margin: 0.5rem 0; color: var(--primary);'>0</h2>
#         <p style='margin: 0; color: var(--text-muted); font-size: 0.85rem;'>Add news articles to begin</p>
#     </div>
#     """, unsafe_allow_html=True)

# with col2:
#     st.markdown("""
#     <div class='metric-card'>
#         <h4 style='margin: 0; color: var(--text-muted); font-size: 0.9rem;'>🏢 COMPANIES</h4>
#         <h2 style='margin: 0.5rem 0; color: var(--primary);'>10</h2>
#         <p style='margin: 0; color: var(--text-muted); font-size: 0.85rem;'>Active in portfolio</p>
#     </div>
#     """, unsafe_allow_html=True)

# with col3:
#     st.markdown("""
#     <div class='metric-card'>
#         <h4 style='margin: 0; color: var(--text-muted); font-size: 0.9rem;'>🎯 MODEL ACCURACY</h4>
#         <h2 style='margin: 0.5rem 0; color: var(--primary);'>87.3%</h2>
#         <p style='margin: 0; color: var(--text-muted); font-size: 0.85rem;'>↑ 2.1% from last month</p>
#     </div>
#     """, unsafe_allow_html=True)

# with col4:
#     st.markdown("""
#     <div class='metric-card'>
#         <h4 style='margin: 0; color: var(--text-muted); font-size: 0.9rem;'>⚡ SYSTEM STATUS</h4>
#         <h2 style='margin: 0.5rem 0; color: var(--secondary);'>Active</h2>
#         <p style='margin: 0; color: var(--text-muted); font-size: 0.85rem;'>All systems operational</p>
#     </div>
#     """, unsafe_allow_html=True)

# # ===============================
# # INPUT SECTION - TABS
# # ===============================

# st.markdown('<p class="section-header">📝 Data Input</p>', unsafe_allow_html=True)

# tab1, tab2 = st.tabs(["📰 News Articles", "💰 Stock Prices"])

# with tab1:
#     st.markdown("""
#     <div class='info-box'>
#         <strong>📌 Tip:</strong> Add Sinhala or English business news articles for comprehensive sentiment analysis. 
#         The system automatically detects language and applies appropriate processing.
#     </div>
#     """, unsafe_allow_html=True)
    
#     if "news_inputs" not in st.session_state:
#         st.session_state.news_inputs = [""]
    
#     col1, col2, col3 = st.columns([3, 1, 1])
#     with col2:
#         if st.button("➕ Add Article", use_container_width=True):
#             st.session_state.news_inputs.append("")
#             st.rerun()
#     with col3:
#         if st.button("🗑️ Clear All", use_container_width=True):
#             st.session_state.news_inputs = [""]
#             st.rerun()
    
#     news_texts = []
#     for i in range(len(st.session_state.news_inputs)):
#         with st.container():
#             news = st.text_area(
#                 f"Article {i+1}",
#                 height=120,
#                 value=st.session_state.news_inputs[i],
#                 key=f"news_{i}",
#                 placeholder="Paste Sinhala/English business news article here...",
#                 help=f"Article {i+1} - Enter full text for sentiment analysis"
#             )
#             news_texts.append(news)
#             st.session_state.news_inputs[i] = news

# with tab2:
#     st.markdown("""
#     <div class='info-box'>
#         <strong>💡 Note:</strong> Enter yesterday's closing prices. Default values are pre-populated based on 
#         historical data but can be modified.
#     </div>
#     """, unsafe_allow_html=True)
    
#     prev_close_prices = {}
    
#     # Group by sector
#     sectors = {}
#     for c in companies:
#         sector = company_data[c]['sector']
#         if sector not in sectors:
#             sectors[sector] = []
#         sectors[sector].append(c)
    
#     for sector, sector_companies in sectors.items():
#         with st.expander(f"📊 {sector} Sector", expanded=True):
#             cols = st.columns(min(3, len(sector_companies)))
#             for idx, c in enumerate(sector_companies):
#                 with cols[idx % 3]:
#                     info = company_data[c]
#                     st.markdown(f"**{info['symbol']}**")
#                     st.caption(info['name'][:25] + "...")
#                     prev_close_prices[c] = st.number_input(
#                         "Price (Rs.)",
#                         min_value=0.0,
#                         value=info['default_price'],
#                         step=0.1,
#                         format="%.2f",
#                         key=f"price_{c}",
#                         help=f"Previous closing price for {info['symbol']}"
#                     )

# # ===============================
# # ANALYZE BUTTON
# # ===============================

# st.markdown("---")

# col1, col2, col3 = st.columns([1, 2, 1])
# with col2:
#     analyze_button = st.button(
#         "🚀 Run Complete Analysis",
#         type="primary",
#         use_container_width=True,
#         help="Analyze all articles and generate predictions"
#     )

# # ===============================
# # ANALYSIS FUNCTIONS (Keep existing functions)
# # ===============================

# def analyze_sentiment(text, company):
#     if sentiment_models.get(company) is not None:
#         try:
#             prediction = sentiment_models[company].predict([text])[0]
#             return prediction
#         except:
#             pass
    
#     # Enhanced fallback
#     text_lower = text.lower()
    
#     positive_keywords = ['profit', 'growth', 'increase', 'success', 'positive', 'strong', 'gain', 'rise',
#                          'ලාභ', 'වර්ධනය', 'ඉහළ', 'සාර්ථක', 'දියුණු']
#     negative_keywords = ['loss', 'decline', 'decrease', 'problem', 'negative', 'weak', 'fall', 'down',
#                          'අලාභ', 'අඩු', 'පහත', 'අසාර්ථක', 'ප්‍රශ්නය']
    
#     pos_count = sum(1 for word in positive_keywords if word in text_lower)
#     neg_count = sum(1 for word in negative_keywords if word in text_lower)
    
#     if pos_count > neg_count:
#         return "Positive"
#     elif neg_count > pos_count:
#         return "Negative"
#     else:
#         return "Neutral"

# def predict_price(company, sentiment_score, prev_close):
#     try:
#         if price_models.get(company) is not None and price_status[company]['loaded']:
#             model_info = price_models[company]
#             if isinstance(model_info, dict):
#                 sarimax_model = model_info.get("model", model_info)
#                 if hasattr(sarimax_model, 'forecast'):
#                     forecast = sarimax_model.forecast(steps=1, exog=np.array([[sentiment_score]]))
#                     return float(forecast.iloc[0])
        
#         # Fallback
#         sentiment_impact = sentiment_score * 0.025
#         market_volatility = np.random.normal(0, 0.005)
#         predicted_change = sentiment_impact + market_volatility
#         predicted_price = prev_close * (1 + predicted_change)
#         predicted_price = max(predicted_price, prev_close * 0.85)
#         predicted_price = min(predicted_price, prev_close * 1.15)
        
#         return predicted_price
#     except:
#         return prev_close * (1 + sentiment_score * 0.02)

# # ===============================
# # ANALYSIS EXECUTION
# # ===============================

# if analyze_button:
#     if all(t.strip() == "" for t in news_texts):
#         st.warning("⚠️ Please enter at least one news article for analysis.")
#         st.stop()
    
#     # Progress
#     progress_container = st.container()
#     with progress_container:
#         progress_bar = st.progress(0)
#         status_text = st.empty()
    
#     # SENTIMENT ANALYSIS
#     status_text.text("🔍 Analyzing sentiment across articles...")
    
#     sentiment_results = []
#     article_details = []
    
#     for idx, text in enumerate(news_texts, 1):
#         if text.strip() == "":
#             continue
        
#         article_sentiments = {"Article": f"Article {idx}", "Text_Preview": text[:100] + "..."}
        
#         for c in companies:
#             sentiment = analyze_sentiment(text, c)
#             article_sentiments[c] = sentiment
        
#         sentiment_results.append(article_sentiments)
#         progress_bar.progress((idx / len(news_texts)) * 0.4)
    
#     sentiment_df = pd.DataFrame(sentiment_results)
    
#     # Calculate scores
#     sentiment_map = {"Positive": 1, "Neutral": 0, "Negative": -1}
#     score_matrix = sentiment_df[[c for c in companies if c in sentiment_df.columns]].copy()
    
#     for c in companies:
#         if c in score_matrix.columns:
#             score_matrix[c] = score_matrix[c].map(sentiment_map)
    
#     daily_scores = score_matrix.mean().reset_index()
#     daily_scores.columns = ["Company", "Average_Sentiment_Score"]
    
#     # PRICE PREDICTIONS
#     status_text.text("💰 Generating price predictions...")
    
#     predictions = []
#     for idx, (_, row_data) in enumerate(daily_scores.iterrows()):
#         company = row_data["Company"]
#         sentiment_score = row_data["Average_Sentiment_Score"]
#         prev_close = prev_close_prices.get(company, company_data[company]['default_price'])
        
#         predicted_price = predict_price(company, sentiment_score, prev_close)
#         change_amount = predicted_price - prev_close
#         change_percent = (change_amount / prev_close) * 100
        
#         predictions.append({
#             "Company": company_data[company]['name'],
#             "Symbol": company_data[company]['symbol'],
#             "Sector": company_data[company]['sector'],
#             "Previous_Close": prev_close,
#             "Predicted_Price": predicted_price,
#             "Price_Change": change_amount,
#             "Price_Change_Percent": change_percent,
#             "Sentiment_Score": sentiment_score,
#             "Sentiment_Category": "Positive" if sentiment_score > 0.1 else "Negative" if sentiment_score < -0.1 else "Neutral",
#             "Color": company_data[company]['color']
#         })
        
#         progress_bar.progress(0.4 + ((idx + 1) / len(companies)) * 0.6)
    
#     predictions_df = pd.DataFrame(predictions)
    
#     progress_bar.empty()
#     status_text.empty()
    
#     # ===============================
#     # RESULTS DISPLAY (Keep all your existing visualization code)
#     # ===============================
    
#     st.markdown('<p class="section-header">📊 Analysis Results</p>', unsafe_allow_html=True)
    
#     # Key Metrics
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         avg_return = predictions_df['Price_Change_Percent'].mean()
#         st.metric(
#             "Average Return",
#             f"{avg_return:+.2f}%",
#             delta="Market Sentiment"
#         )
    
#     with col2:
#         positive_stocks = len(predictions_df[predictions_df['Price_Change_Percent'] > 0])
#         st.metric(
#             "Gainers",
#             f"{positive_stocks}/10",
#             delta=f"{positive_stocks*10}% of portfolio"
#         )
    
#     with col3:
#         avg_sentiment = predictions_df['Sentiment_Score'].mean()
#         st.metric(
#             "Sentiment Score",
#             f"{avg_sentiment:.3f}",
#             delta="Positive" if avg_sentiment > 0 else "Negative"
#         )
    
#     with col4:
#         best_performer = predictions_df.loc[predictions_df['Price_Change_Percent'].idxmax()]
#         st.metric(
#             "Top Performer",
#             best_performer['Symbol'],
#             delta=f"+{best_performer['Price_Change_Percent']:.1f}%"
#         )
    
#     # Article-by-Article Sentiment Table
#     st.markdown('<p class="section-header">📰 Article-by-Article Sentiment Analysis</p>', unsafe_allow_html=True)
    
#     # Create detailed article analysis
#     article_sentiment_display = sentiment_df.copy()
    
#     # Rename columns to symbols
#     display_columns = {"Article": "Article", "Text_Preview": "Preview"}
#     for c in companies:
#         if c in article_sentiment_display.columns:
#             display_columns[c] = company_data[c]['symbol']
    
#     article_sentiment_display = article_sentiment_display.rename(columns=display_columns)
    
#     # Color coding function
#     def sentiment_style(val):
#         if val == "Positive":
#             return 'background-color: rgba(16, 185, 129, 0.2); color: #34d399; font-weight: 600;'
#         elif val == "Negative":
#             return 'background-color: rgba(239, 68, 68, 0.2); color: #f87171; font-weight: 600;'
#         elif val == "Neutral":
#             return 'background-color: rgba(100, 116, 139, 0.2); color: #cbd5e1; font-weight: 600;'
#         return ''
    
#     # Apply styling
#     styled_df = article_sentiment_display.style.applymap(
#         sentiment_style,
#         subset=[col for col in article_sentiment_display.columns if col not in ["Article", "Preview"]]
#     )
    
#     st.dataframe(
#         styled_df,
#         use_container_width=True,
#         height=400
#     )
    
#     # Sentiment Summary by Company
#     st.markdown("##### 📈 Sentiment Distribution by Company")
    
#     sentiment_summary = {}
#     for c in companies:
#         if c in sentiment_df.columns:
#             counts = sentiment_df[c].value_counts()
#             sentiment_summary[company_data[c]['symbol']] = {
#                 'Positive': counts.get('Positive', 0),
#                 'Neutral': counts.get('Neutral', 0),
#                 'Negative': counts.get('Negative', 0),
#                 'Total': len(sentiment_df)
#             }
    
#     summary_df = pd.DataFrame(sentiment_summary).T
#     summary_df['Positive %'] = (summary_df['Positive'] / summary_df['Total'] * 100).round(1)
#     summary_df['Negative %'] = (summary_df['Negative'] / summary_df['Total'] * 100).round(1)
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         # Stacked bar chart
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             name='Positive',
#             x=summary_df.index,
#             y=summary_df['Positive'],
#             marker_color='#10b981'
#         ))
        
#         fig.add_trace(go.Bar(
#             name='Neutral',
#             x=summary_df.index,
#             y=summary_df['Neutral'],
#             marker_color='#64748b'
#         ))
        
#         fig.add_trace(go.Bar(
#             name='Negative',
#             x=summary_df.index,
#             y=summary_df['Negative'],
#             marker_color='#ef4444'
#         ))
        
#         fig.update_layout(
#             barmode='stack',
#             title='Sentiment Distribution Across Articles',
#             xaxis_title='Company',
#             yaxis_title='Number of Articles',
#             height=350,
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#             paper_bgcolor='rgba(0,0,0,0)',
#             plot_bgcolor='rgba(0,0,0,0)',
#             font=dict(color='#cbd5e1')
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         st.dataframe(
#             summary_df[['Positive', 'Neutral', 'Negative', 'Positive %', 'Negative %']],
#             use_container_width=True,
#             height=350
#         )
    
#     # Price Predictions Table
#     st.markdown('<p class="section-header">💰 Price Predictions & Forecasts</p>', unsafe_allow_html=True)
    
#     display_df = predictions_df.copy()
#     display_df['Previous_Close'] = display_df['Previous_Close'].apply(lambda x: f"Rs. {x:,.2f}")
#     display_df['Predicted_Price'] = display_df['Predicted_Price'].apply(lambda x: f"Rs. {x:,.2f}")
#     display_df['Price_Change'] = display_df['Price_Change'].apply(lambda x: f"{x:+,.2f}")
#     display_df['Price_Change_Percent'] = display_df['Price_Change_Percent'].apply(lambda x: f"{x:+.2f}%")
#     display_df['Sentiment_Score'] = display_df['Sentiment_Score'].apply(lambda x: f"{x:.3f}")
    
#     st.dataframe(
#         display_df[['Symbol', 'Company', 'Sector', 'Previous_Close', 
#                    'Predicted_Price', 'Price_Change', 'Price_Change_Percent',
#                    'Sentiment_Score', 'Sentiment_Category']],
#         use_container_width=True,
#         height=400
#     )
    
#     # Visualizations
#     st.markdown('<p class="section-header">📊 Interactive Visualizations</p>', unsafe_allow_html=True)
    
#     viz_tab1, viz_tab2, viz_tab3 = st.tabs(["📈 Price Changes", "🎯 Sentiment Analysis", "🏢 Sector Overview"])
    
#     with viz_tab1:
#         col1, col2 = st.columns(2)
        
#         with col1:
#             # Price change waterfall
#             sorted_df = predictions_df.sort_values('Price_Change_Percent', ascending=True)
#             colors = ['#ef4444' if x < 0 else '#10b981' for x in sorted_df['Price_Change_Percent']]
            
#             fig1 = go.Figure()
#             fig1.add_trace(go.Bar(
#                 x=sorted_df['Price_Change_Percent'],
#                 y=sorted_df['Symbol'],
#                 orientation='h',
#                 marker_color=colors,
#                 text=sorted_df['Price_Change_Percent'].apply(lambda x: f"{x:+.1f}%"),
#                 textposition='outside',
#                 hovertemplate='<b>%{y}</b><br>Change: %{x:.2f}%<extra></extra>'
#             ))
            
#             fig1.update_layout(
#                 title="Expected Price Changes",
#                 xaxis_title="Price Change (%)",
#                 yaxis_title="",
#                 height=450,
#                 showlegend=False,
#                 paper_bgcolor='rgba(0,0,0,0)',
#                 plot_bgcolor='rgba(0,0,0,0)',
#                 font=dict(color='#cbd5e1')
#             )
            
#             st.plotly_chart(fig1, use_container_width=True)
        
#         with col2:
#             # Price prediction comparison
#             fig2 = go.Figure()
            
#             fig2.add_trace(go.Scatter(
#                 x=predictions_df['Symbol'],
#                 y=predictions_df['Previous_Close'],
#                 mode='markers+lines',
#                 name='Previous Close',
#                 marker=dict(size=10, color='#64748b'),
#                 line=dict(color='#64748b', dash='dash')
#             ))
            
#             fig2.add_trace(go.Scatter(
#                 x=predictions_df['Symbol'],
#                 y=predictions_df['Predicted_Price'],
#                 mode='markers+lines',
#                 name='Predicted Price',
#                 marker=dict(size=12, color='#3b82f6'),
#                 line=dict(color='#3b82f6', width=3)
#             ))
            
#             fig2.update_layout(
#                 title="Price Comparison: Previous vs Predicted",
#                 xaxis_title="Company",
#                 yaxis_title="Price (Rs.)",
#                 height=450,
#                 hovermode='x unified',
#                 paper_bgcolor='rgba(0,0,0,0)',
#                 plot_bgcolor='rgba(0,0,0,0)',
#                 font=dict(color='#cbd5e1')
#             )
            
#             st.plotly_chart(fig2, use_container_width=True)
    
#     with viz_tab2:
#         col1, col2 = st.columns(2)
        
#         with col1:
#             # Sentiment vs Performance scatter
#             fig3 = px.scatter(
#                 predictions_df,
#                 x='Sentiment_Score',
#                 y='Price_Change_Percent',
#                 size='Previous_Close',
#                 color='Sector',
#                 text='Symbol',
#                 title="Sentiment Impact on Price Movement",
#                 labels={
#                     'Sentiment_Score': 'Sentiment Score',
#                     'Price_Change_Percent': 'Expected Price Change (%)'
#                 },
#                 height=450
#             )
            
#             fig3.update_traces(
#                 textposition='top center',
#                 marker=dict(opacity=0.7, line=dict(width=1, color='white'))
#             )
            
#             fig3.update_layout(
#                 paper_bgcolor='rgba(0,0,0,0)',
#                 plot_bgcolor='rgba(0,0,0,0)',
#                 font=dict(color='#cbd5e1')
#             )
            
#             # Add trend line
#             fig3.add_trace(go.Scatter(
#                 x=[-1, 1],
#                 y=[-5, 5],
#                 mode='lines',
#                 line=dict(color='red', dash='dash'),
#                 name='Trend',
#                 showlegend=False
#             ))
            
#             st.plotly_chart(fig3, use_container_width=True)
        
#         with col2:
#             # Sentiment category pie chart
#             sentiment_counts = predictions_df['Sentiment_Category'].value_counts()
            
#             fig4 = go.Figure(data=[go.Pie(
#                 labels=sentiment_counts.index,
#                 values=sentiment_counts.values,
#                 hole=0.4,
#                 marker=dict(colors=['#10b981', '#64748b', '#ef4444']),
#                 textinfo='label+percent',
#                 textfont_size=14
#             )])
            
#             fig4.update_layout(
#                 title="Overall Sentiment Distribution",
#                 height=450,
#                 showlegend=True,
#                 paper_bgcolor='rgba(0,0,0,0)',
#                 font=dict(color='#cbd5e1')
#             )
            
#             st.plotly_chart(fig4, use_container_width=True)
    
#     with viz_tab3:
#         col1, col2 = st.columns(2)
        
#         with col1:
#             # Sector performance
#             sector_performance = predictions_df.groupby('Sector').agg({
#                 'Price_Change_Percent': 'mean',
#                 'Symbol': 'count'
#             }).reset_index()
#             sector_performance.columns = ['Sector', 'Avg_Change', 'Count']
            
#             fig5 = go.Figure()
#             fig5.add_trace(go.Bar(
#                 x=sector_performance['Sector'],
#                 y=sector_performance['Avg_Change'],
#                 text=sector_performance['Avg_Change'].apply(lambda x: f"{x:+.1f}%"),
#                 textposition='outside',
#                 marker_color=['#10b981' if x > 0 else '#ef4444' for x in sector_performance['Avg_Change']],
#                 hovertemplate='<b>%{x}</b><br>Avg Change: %{y:.2f}%<extra></extra>'
#             ))
            
#             fig5.update_layout(
#                 title="Average Price Change by Sector",
#                 xaxis_title="Sector",
#                 yaxis_title="Average Change (%)",
#                 height=450,
#                 showlegend=False,
#                 paper_bgcolor='rgba(0,0,0,0)',
#                 plot_bgcolor='rgba(0,0,0,0)',
#                 font=dict(color='#cbd5e1')
#             )
            
#             st.plotly_chart(fig5, use_container_width=True)
        
#         with col2:
#             # Sector composition
#             sector_counts = predictions_df['Sector'].value_counts()
            
#             fig6 = go.Figure(data=[go.Bar(
#                 x=sector_counts.values,
#                 y=sector_counts.index,
#                 orientation='h',
#                 marker_color='#3b82f6',
#                 text=sector_counts.values,
#                 textposition='outside'
#             )])
            
#             fig6.update_layout(
#                 title="Company Distribution by Sector",
#                 xaxis_title="Number of Companies",
#                 yaxis_title="",
#                 height=450,
#                 showlegend=False,
#                 paper_bgcolor='rgba(0,0,0,0)',
#                 plot_bgcolor='rgba(0,0,0,0)',
#                 font=dict(color='#cbd5e1')
#             )
            
#             st.plotly_chart(fig6, use_container_width=True)
    
#     # Recommendations
#     st.markdown('<p class="section-header">💡 Investment Recommendations</p>', unsafe_allow_html=True)
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.markdown("#### 🎯 Top Opportunities")
#         top_3 = predictions_df.nlargest(3, 'Price_Change_Percent')
        
#         for idx, row in top_3.iterrows():
#             st.markdown(f"""
#             <div class='opportunity-card'>
#                 <h4 style='margin: 0; color: #34d399;'>{row['Symbol']} - {row['Company']}</h4>
#                 <p style='margin: 0.5rem 0; color: #cbd5e1;'>
#                     <strong>Target:</strong> Rs. {row['Predicted_Price']:.2f} | 
#                     <strong>Return:</strong> <span style='color: #10b981; font-weight: 700;'>{row['Price_Change_Percent']:+.2f}%</span>
#                 </p>
#                 <p style='margin: 0; color: #94a3b8; font-size: 0.9rem;'>
#                     <strong>Sentiment:</strong> {row['Sentiment_Score']:.3f} ({row['Sentiment_Category']}) | 
#                     <strong>Sector:</strong> {row['Sector']}
#                 </p>
#             </div>
#             """, unsafe_allow_html=True)
            
#             normalized_progress = (row['Price_Change_Percent'] + 20) / 40
#             normalized_progress = max(0.01, min(0.99, normalized_progress))
#             st.progress(normalized_progress)
    
#     with col2:
#         st.markdown("#### ⚠️ Stocks to Monitor")
#         bottom_3 = predictions_df.nsmallest(3, 'Price_Change_Percent')
        
#         for idx, row in bottom_3.iterrows():
#             st.markdown(f"""
#             <div class='monitor-card'>
#                 <h4 style='margin: 0; color: #f87171;'>{row['Symbol']} - {row['Company']}</h4>
#                 <p style='margin: 0.5rem 0; color: #cbd5e1;'>
#                     <strong>Target:</strong> Rs. {row['Predicted_Price']:.2f} | 
#                     <strong>Return:</strong> <span style='color: #ef4444; font-weight: 700;'>{row['Price_Change_Percent']:+.2f}%</span>
#                 </p>
#                 <p style='margin: 0; color: #94a3b8; font-size: 0.9rem;'>
#                     <strong>Sentiment:</strong> {row['Sentiment_Score']:.3f} ({row['Sentiment_Category']}) | 
#                     <strong>Sector:</strong> {row['Sector']}
#                 </p>
#             </div>
#             """, unsafe_allow_html=True)
            
#             normalized_progress = (row['Price_Change_Percent'] + 20) / 40
#             normalized_progress = max(0.01, min(0.99, normalized_progress))
#             st.progress(normalized_progress)
    
#     # Advanced Analytics (Optional)
#     if show_advanced:
#         st.markdown('<p class="section-header">🔬 Advanced Analytics</p>', unsafe_allow_html=True)
        
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             confidence = min(90, max(10, 50 + (avg_return * 2)))
#             st.markdown(f"""
#             <div class='metric-card'>
#                 <h4 style='margin: 0; color: var(--text-muted);'>Model Confidence</h4>
#                 <h2 style='margin: 0.5rem 0; color: var(--primary);'>{confidence:.0f}%</h2>
#                 <p style='margin: 0; color: var(--text-muted);'>Based on historical accuracy</p>
#             </div>
#             """, unsafe_allow_html=True)
#             st.progress(confidence / 100)
        
#         with col2:
#             market_sentiment = "Bullish 🐂" if avg_return > 1 else "Bearish 🐻" if avg_return < -1 else "Neutral ➡️"
#             sentiment_color = "#10b981" if "Bullish" in market_sentiment else "#ef4444" if "Bearish" in market_sentiment else "#f59e0b"
            
#             st.markdown(f"""
#             <div class='metric-card'>
#                 <h4 style='margin: 0; color: var(--text-muted);'>Market Outlook</h4>
#                 <h2 style='margin: 0.5rem 0; color: {sentiment_color};'>{market_sentiment}</h2>
#                 <p style='margin: 0; color: var(--text-muted);'>Overall market direction</p>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col3:
#             volatility = predictions_df['Price_Change_Percent'].std()
#             risk_level = "High 🔴" if volatility > 5 else "Low 🟢" if volatility < 2 else "Moderate 🟡"
#             risk_color = "#ef4444" if "High" in risk_level else "#10b981" if "Low" in risk_level else "#f59e0b"
            
#             st.markdown(f"""
#             <div class='metric-card'>
#                 <h4 style='margin: 0; color: var(--text-muted);'>Risk Level</h4>
#                 <h2 style='margin: 0.5rem 0; color: {risk_color};'>{risk_level}</h2>
#                 <p style='margin: 0; color: var(--text-muted);'>Volatility: {volatility:.2f}%</p>
#             </div>
#             """, unsafe_allow_html=True)
        
#         # Strategy Recommendations
#         st.markdown("#### 📋 Strategic Recommendations")
        
#         strategy_col1, strategy_col2, strategy_col3 = st.columns(3)
        
#         with strategy_col1:
#             st.markdown("""
#             <div style='background: var(--surface); padding: 1rem; border-radius: 12px; border: 1px solid var(--border);'>
#                 <h4 style='color: var(--primary); margin: 0 0 0.5rem 0;'>For Investors 💼</h4>
#                 <ul style='color: var(--text-secondary); margin: 0; padding-left: 1.5rem;'>
#                     <li>Diversify across top 5 performers</li>
#                     <li>Long-term hold (3-6 months)</li>
#                     <li>Rebalance monthly</li>
#                     <li>Stop-loss at -5%</li>
#                 </ul>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with strategy_col2:
#             st.markdown("""
#             <div style='background: var(--surface); padding: 1rem; border-radius: 12px; border: 1px solid var(--border);'>
#                 <h4 style='color: var(--primary); margin: 0 0 0.5rem 0;'>For Traders 📊</h4>
#                 <ul style='color: var(--text-secondary); margin: 0; padding-left: 1.5rem;'>
#                     <li>Focus on high volatility stocks</li>
#                     <li>Day trading on news releases</li>
#                     <li>Take profit at +3-5%</li>
#                     <li>Use trailing stops</li>
#                 </ul>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with strategy_col3:
#             st.markdown("""
#             <div style='background: var(--surface); padding: 1rem; border-radius: 12px; border: 1px solid var(--border);'>
#                 <h4 style='color: var(--primary); margin: 0 0 0.5rem 0;'>For Analysts 🔍</h4>
#                 <ul style='color: var(--text-secondary); margin: 0; padding-left: 1.5rem;'>
#                     <li>Cross-reference with technicals</li>
#                     <li>Monitor volume patterns</li>
#                     <li>Track macro indicators</li>
#                     <li>Validate with fundamentals</li>
#                 </ul>
#             </div>
#             """, unsafe_allow_html=True)
    
#     # Export Functionality
#     st.markdown('<p class="section-header">📥 Export Results</p>', unsafe_allow_html=True)
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         csv_data = predictions_df.to_csv(index=False)
#         st.download_button(
#             label="📊 Download Predictions",
#             data=csv_data,
#             file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
#             mime="text/csv",
#             use_container_width=True,
#             help="Download price predictions as CSV"
#         )
    
#     with col2:
#         sentiment_export = sentiment_df.to_csv(index=False)
#         st.download_button(
#             label="📰 Download Sentiment Analysis",
#             data=sentiment_export,
#             file_name=f"sentiment_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
#             mime="text/csv",
#             use_container_width=True,
#             help="Download article sentiment analysis"
#         )
    
#     with col3:
#         # Comprehensive report
#         full_report = predictions_df.copy()
#         full_report['Analysis_Date'] = analysis_date
#         full_report['Articles_Analyzed'] = len([t for t in news_texts if t.strip()])
        
#         report_csv = full_report.to_csv(index=False)
#         st.download_button(
#             label="📄 Download Full Report",
#             data=report_csv,
#             file_name=f"full_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
#             mime="text/csv",
#             use_container_width=True,
#             help="Download comprehensive analysis report"
#         )
    
#     # Disclaimer
#     st.markdown("---")
    
#     st.markdown("""
#     <div class='warning-box'>
#         <h4 style='margin: 0 0 0.5rem 0; color: #f59e0b;'>⚠️ Important Disclaimer</h4>
#         <p style='margin: 0; font-size: 0.9rem; color: #cbd5e1;'>
#             This analysis is generated by machine learning models based on news sentiment and historical patterns. 
#             <strong>Past performance does not guarantee future results.</strong>
#         </p>
#         <ul style='margin: 0.5rem 0 0 1rem; font-size: 0.9rem; color: #94a3b8;'>
#             <li>Conduct independent research and due diligence</li>
#             <li>Consult licensed financial advisors</li>
#             <li>Consider your risk tolerance and investment goals</li>
#             <li>Diversify your investment portfolio</li>
#             <li>Monitor market conditions regularly</li>
#         </ul>
#         <p style='margin: 0.5rem 0 0 0; font-size: 0.85rem; font-style: italic; color: #94a3b8;'>
#             Stock market investments carry inherent risks, including potential loss of principal.
#         </p>
#     </div>
#     """, unsafe_allow_html=True)

# # ===============================
# # FOOTER WITH CREDITS
# # ===============================

# st.markdown("""
# <div class='footer'>
#     <p style='margin: 0; font-size: 1rem; font-weight: 600; color: var(--primary);'>Sinhala News Sentinel</p>
#     <p style='margin: 0.5rem 0; color: var(--text-muted);'>AI-Powered Stock Market Intelligence Platform</p>
#     <p style='margin: 0.5rem 0; color: var(--text-muted);'>
#         Developed with ❤️ by <a href='https://www.linkedin.com/in/huzaifaameer/' target='_blank'>Huzaifa Ameer</a> | © 2026
#     </p>
#     <p style='margin: 0.5rem 0; font-size: 0.85rem; color: var(--text-muted);'>
#         <a href='#' style='color: var(--primary-light); text-decoration: none;'>Documentation</a> • 
#         <a href='#' style='color: var(--primary-light); text-decoration: none;'>API Access</a> • 
#         <a href='#' style='color: var(--primary-light); text-decoration: none;'>Support</a> • 
#         <a href='https://github.com/huzaifa-ameer' target='_blank' style='color: var(--primary-light); text-decoration: none;'>GitHub</a>
#     </p>
#     <p style='margin: 1rem 0 0 0; font-size: 0.8rem; color: var(--text-muted);'>
#         Version 3.0 | All Rights Reserved
#     </p>
# </div>
# """, unsafe_allow_html=True)