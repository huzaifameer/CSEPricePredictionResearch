# import streamlit as st
# import pandas as pd
# import joblib
# import numpy as np
# import re
# import os
# import json
# import plotly.graph_objects as go
# import plotly.express as px
# from datetime import datetime, timedelta
# import warnings
# warnings.filterwarnings('ignore')
# from huggingface_hub import snapshot_download
# import tempfile

# # ===============================
# # HUGGING FACE MODEL DOWNLOAD - FIXED
# # ===============================

# @st.cache_resource
# def download_models():
#     """
#     Download models from Hugging Face with correct repo ID format
#     """
#     # CORRECT FORMAT: "username/repo_name" (no extra slashes)
#     REPO_ID = "huzaifaameer/sinhala-news-sentinel"  # Fixed: removed duplicate username
    
#     try:
#         # Create a temporary directory to store models
#         with tempfile.TemporaryDirectory() as tmpdir:
#             st.info("📥 Downloading models from Hugging Face... This may take a moment.")
            
#             # Download the entire repository
#             local_dir = snapshot_download(
#                 repo_id=REPO_ID,
#                 repo_type="space",
#                 local_dir=os.path.join(tmpdir, "models"),
#                 local_dir_use_symlinks=False
#             )
            
#             st.success("✅ Models downloaded successfully!")
#             return local_dir
            
#     except Exception as e:
#         st.error(f"❌ Failed to download models: {str(e)}")
#         st.warning("⚠️ Using local models instead. Make sure they exist in the correct paths.")
        
#         # Fallback to local paths
#         return "."  # Current directory

# # Try to download models, fallback to local if fails
# try:
#     BASE_PATH = download_models()
# except:
#     BASE_PATH = "."
#     st.warning("⚠️ Using local models. Ensure 'saved_models/' and 'price_models_final_v3/' exist.")

# # Set model paths
# SENTIMENT_MODEL_PATH = os.path.join(BASE_PATH, "saved_models")
# PRICE_MODEL_PATH = os.path.join(BASE_PATH, "price_models_final_v3")

# # Alternative: If you want to use a persistent local directory instead of temp
# @st.cache_resource
# def download_models_persistent():
#     """
#     Download models to a persistent local cache directory
#     """
#     REPO_ID = "huzaifaameer/sinhala-news-sentinel"
    
#     # Create a persistent cache directory in the user's home
#     cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "sinhala-news-sentinel")
#     os.makedirs(cache_dir, exist_ok=True)
    
#     model_path = os.path.join(cache_dir, "models")
    
#     # Only download if not already present
#     if not os.path.exists(model_path) or not os.listdir(model_path):
#         st.info("📥 Downloading models from Hugging Face... This may take a moment.")
#         local_dir = snapshot_download(
#             repo_id=REPO_ID,
#             repo_type="space",
#             local_dir=model_path,
#             local_dir_use_symlinks=False
#         )
#         st.success("✅ Models downloaded successfully!")
#     else:
#         st.info("✅ Using cached models from previous download.")
    
#     return model_path

# # Use persistent download (better for production)
# try:
#     MODEL_CACHE_PATH = download_models_persistent()
#     SENTIMENT_MODEL_PATH = os.path.join(MODEL_CACHE_PATH, "saved_models")
#     PRICE_MODEL_PATH = os.path.join(MODEL_CACHE_PATH, "price_models_final_v3")
# except Exception as e:
#     st.error(f"❌ Model download failed: {str(e)}")
#     st.stop()

# # ===============================
# # PAGE CONFIG
# # ===============================

# st.set_page_config(
#     page_title="SentiTrade",
#     page_icon="📰",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ===============================
# # LANGUAGE HELPER — must be initialised before any UI
# # ===============================

# if "lang" not in st.session_state:
#     st.session_state.lang = "si"   # default: Sinhala

# def t(si_text, en_text):
#     """Return si_text or en_text based on current language setting."""
#     return si_text if st.session_state.lang == "si" else en_text

# # ===============================
# # REFINED THEME & STYLING
# # ===============================

# st.markdown("""
# <style>
#     /* ── Fonts ── */
#     @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Sinhala:wght@300;400;500;600;700&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=DM+Mono:wght@400;500&display=swap');

#     /* ── Design Tokens ── */
#     :root {
#         --bg:           #07101f;
#         --surface:      #0e1929;
#         --surface-2:    #152135;
#         --surface-3:    #1b2d45;
#         --border:       #223048;
#         --border-soft:  #182840;

#         --indigo:       #6473f3;
#         --indigo-dim:   rgba(100,115,243,0.14);
#         --indigo-glow:  rgba(100,115,243,0.32);
#         --indigo-light: #a5b4fc;
#         --emerald:      #10c98a;
#         --amber:        #f5b731;
#         --rose:         #f05c6e;

#         --txt-1: #e6ecf5;
#         --txt-2: #8fa5c2;
#         --txt-3: #4d637f;

#         --r:  14px;
#         --rl: 20px;
#         --shadow: 0 6px 30px rgba(0,0,0,0.5);
#     }

#     /* ── Base ── */
#     html, body, [class*="css"] {
#         font-family: 'DM Sans', 'Noto Sans Sinhala', sans-serif !important;
#         background: var(--bg) !important;
#         color: var(--txt-1) !important;
#     }
#     h1,h2,h3,h4,h5,h6 { font-family: 'DM Sans','Noto Sans Sinhala',sans-serif; }
#     code, pre           { font-family: 'DM Mono', monospace; }
#     #MainMenu, footer, header { visibility: hidden; }

#     /* ── Scrollbar ── */
#     ::-webkit-scrollbar { width:6px; height:6px; }
#     ::-webkit-scrollbar-track  { background: var(--surface); }
#     ::-webkit-scrollbar-thumb  { background: var(--indigo); border-radius:3px; }

#     /* ── HERO ── */
#     .hero {
#         background: linear-gradient(140deg, var(--surface-2) 0%, var(--bg) 100%);
#         border: 1px solid var(--border);
#         border-radius: var(--rl);
#         padding: 2.5rem 2.5rem 2.2rem;
#         position: relative; overflow: hidden;
#         margin-bottom: 1.5rem;
#     }
#     .hero::before {
#         content:''; position:absolute; inset:0;
#         background: radial-gradient(ellipse 55% 65% at 85% 45%,
#             rgba(100,115,243,0.09) 0%, transparent 70%);
#         pointer-events:none;
#     }
#     .hero-badge {
#         display:inline-flex; align-items:center; gap:6px;
#         background:var(--indigo-dim); border:1px solid rgba(100,115,243,0.4);
#         color:var(--indigo-light); font-size:0.7rem; font-weight:700;
#         letter-spacing:0.1em; text-transform:uppercase;
#         padding:3px 11px; border-radius:20px; margin-bottom:0.9rem;
#     }
#     .hero-title {
#         font-size: clamp(1.85rem,3.2vw,2.7rem);
#         font-weight:700; color:var(--txt-1);
#         margin:0 0 0.45rem; line-height:1.15; letter-spacing:-0.5px;
#     }
#     .hero-title span {
#         background: linear-gradient(90deg, var(--indigo) 0%, #a78bfa 100%);
#         -webkit-background-clip:text; -webkit-text-fill-color:transparent;
#     }
#     .hero-sub {
#         color:var(--txt-2); font-size:0.93rem;
#         margin:0; line-height:1.7; max-width:640px;
#     }
#     .hero-meta {
#         position:absolute; bottom:1.2rem; right:1.8rem;
#         color:var(--txt-3); font-size:0.78rem;
#     }
#     .hero-meta a { color:var(--indigo); text-decoration:none; font-weight:600; }

#     /* ── SYSTEM CARD ── */
#     .sys-card {
#         background: var(--surface-2); border:1px solid var(--border);
#         border-radius:var(--rl); padding:1.75rem 1.75rem 1.5rem;
#         margin-bottom:1.75rem; position:relative; overflow:hidden;
#     }
#     .sys-card::after {
#         content:''; position:absolute; top:0; left:0;
#         width:4px; height:100%;
#         background: linear-gradient(180deg, var(--indigo) 0%, #a78bfa 100%);
#     }
#     .sys-card h3 {
#         color:var(--txt-1); font-size:1.05rem;
#         margin:0 0 0.7rem; font-weight:700;
#     }
#     .sys-card p  { color:var(--txt-2); font-size:0.88rem; line-height:1.75; margin:0 0 0.5rem; }
#     .sys-card ul { color:var(--txt-2); padding-left:1.35rem; margin:0.4rem 0 0; }
#     .sys-card li { font-size:0.87rem; line-height:2.1; }
#     .sys-card li strong { color:var(--txt-1); }
#     .sys-divider { border:none; border-top:1px solid var(--border-soft); margin:0.8rem 0; }

#     /* ── SECTION HEADERS ── */
#     .sec-hdr {
#         display:flex; align-items:center; gap:10px;
#         font-size:1.05rem; font-weight:700; color:var(--txt-1);
#         margin:2rem 0 1rem; padding-bottom:0.6rem;
#         border-bottom:1px solid var(--border);
#     }
#     .sec-dot {
#         width:8px; height:8px; border-radius:50%;
#         background:var(--indigo); flex-shrink:0;
#         box-shadow:0 0 8px var(--indigo-glow);
#     }

#     /* ── INFO / WARNING BOXES ── */
#     .info-box {
#         background:var(--indigo-dim); border:1px solid rgba(100,115,243,0.3);
#         border-radius:var(--r); padding:0.9rem 1.1rem;
#         margin:0.9rem 0; color:var(--txt-2); font-size:0.87rem; line-height:1.75;
#     }
#     .info-box strong { color:var(--indigo-light); }
#     .warn-box {
#         background:rgba(245,183,49,0.07); border:1px solid rgba(245,183,49,0.28);
#         border-radius:var(--r); padding:0.9rem 1.1rem;
#         margin:0.9rem 0; color:var(--txt-2); font-size:0.87rem; line-height:1.75;
#     }
#     .warn-box strong { color:var(--amber); }

#     /* ── OPPORTUNITY / MONITOR CARDS ── */
#     .opp-card {
#         background:rgba(16,201,138,0.07); border:1px solid rgba(16,201,138,0.22);
#         border-radius:var(--r); padding:1.1rem 1.2rem; margin-bottom:0.7rem;
#     }
#     .opp-card h4 { color:var(--emerald); margin:0 0 0.35rem; font-size:0.93rem; }
#     .mon-card {
#         background:rgba(240,92,110,0.07); border:1px solid rgba(240,92,110,0.22);
#         border-radius:var(--r); padding:1.1rem 1.2rem; margin-bottom:0.7rem;
#     }
#     .mon-card h4 { color:var(--rose); margin:0 0 0.35rem; font-size:0.93rem; }
#     .c-row  { color:var(--txt-2); font-size:0.83rem; margin:0.2rem 0; }
#     .c-row strong { color:var(--txt-1); }
#     .tg  { color:var(--emerald); font-weight:700; }
#     .tr  { color:var(--rose);    font-weight:700; }

#     /* ── STATUS DOTS ── */
#     .dot { width:9px;height:9px;border-radius:50%;display:inline-block;margin-right:6px;vertical-align:middle; }
#     .dot-on  { background:var(--emerald); box-shadow:0 0 5px rgba(16,201,138,0.55); }
#     .dot-off { background:var(--rose);    box-shadow:0 0 5px rgba(240,92,110,0.45); }

#     /* ── FOOTER ── */
#     .footer {
#         text-align:center; padding:2.5rem 0 1rem;
#         border-top:1px solid var(--border); margin-top:3rem;
#         color:var(--txt-3); font-size:0.8rem; line-height:2.1;
#     }
#     .footer a { color:var(--indigo); text-decoration:none; font-weight:600; }
#     .footer strong { color:var(--txt-2); }

#     /* ── Streamlit overrides ── */
#     .main { background:var(--bg) !important; }

#     [data-testid="stSidebar"] {
#         background:var(--surface) !important;
#         border-right:1px solid var(--border) !important;
#     }

#     .stTextArea textarea {
#         background:var(--surface-2) !important; color:var(--txt-1) !important;
#         border:1px solid var(--border) !important; border-radius:var(--r) !important;
#         font-family:'Noto Sans Sinhala','DM Sans',sans-serif !important;
#         font-size:0.91rem !important; line-height:1.7 !important;
#     }
#     .stTextArea textarea:focus {
#         border-color:var(--indigo) !important;
#         box-shadow:0 0 0 3px var(--indigo-dim) !important;
#     }
#     .stTextArea textarea::placeholder { color:var(--txt-3) !important; }

#     .stButton > button {
#         background:linear-gradient(135deg, var(--indigo) 0%, #4f46e5 100%) !important;
#         color:#fff !important; border:none !important;
#         border-radius:var(--r) !important; font-weight:600 !important;
#         font-size:0.87rem !important; padding:0.65rem 1.35rem !important;
#         transition:all 0.2s !important; letter-spacing:0.02em;
#     }
#     .stButton > button:hover {
#         transform:translateY(-2px) !important;
#         box-shadow:0 8px 22px var(--indigo-glow) !important;
#     }

#     .stNumberInput input {
#         background:var(--surface-2) !important; color:var(--txt-1) !important;
#         border:1px solid var(--border) !important; border-radius:8px !important;
#     }

#     .stTabs [data-baseweb="tab-list"] {
#         gap:5px; background:var(--surface-2);
#         padding:5px; border-radius:var(--r); border:1px solid var(--border);
#     }
#     .stTabs [data-baseweb="tab"] {
#         background:transparent !important; color:var(--txt-2) !important;
#         border-radius:10px !important; padding:0.55rem 1.2rem !important;
#         font-weight:500; font-size:0.86rem;
#     }
#     .stTabs [aria-selected="true"] {
#         background:var(--indigo) !important; color:#fff !important;
#     }

#     .streamlit-expanderHeader {
#         background:var(--surface-2) !important; color:var(--txt-1) !important;
#         border:1px solid var(--border) !important; border-radius:var(--r) !important;
#     }

#     .stProgress > div > div {
#         background:linear-gradient(90deg, var(--indigo) 0%, var(--emerald) 100%);
#         border-radius:4px; height:5px !important;
#     }

#     .dataframe { background:var(--surface-2) !important; border-radius:var(--r) !important; }
#     .dataframe th {
#         background:var(--surface-3) !important; color:var(--txt-1) !important;
#         font-weight:600 !important; padding:0.65rem !important;
#     }
#     .dataframe td {
#         background:var(--surface-2) !important; color:var(--txt-2) !important;
#         padding:0.65rem !important; border-bottom:1px solid var(--border-soft) !important;
#     }
# </style>
# """, unsafe_allow_html=True)

# # ===============================
# # DATA & CONFIG
# # ===============================

# STOPWORDS_PATH      = "./data/stop words.txt"

# @st.cache_resource
# def load_stopwords():
#     if not os.path.exists(STOPWORDS_PATH):
#         st.error("⚠️ Stopwords file not found.")
#         return []
#     return open(STOPWORDS_PATH, encoding="utf-8").read().splitlines()

# stop_words = load_stopwords()

# def tokenizer(text):
#     tokens = re.findall(r'\b\w+\b', text.lower())
#     return [tk for tk in tokens if tk not in stop_words]

# # ── Companies ────────────────────────────────────────────────────────────────

# companies = [
#     "MCPL.N0000","WATA.N0000","AGPL.N0000","HAPU.N0000",
#     "KOTA.N0000","BFL.N0000","RWSL.N0000","DIPP.N0000",
#     "MGT.N0000","HEXP.N0000"
# ]

# BEST_MODELS = {c: 'XGBoost' for c in companies}

# MODEL_METRICS = {
#     'MCPL.N0000': {'XGBoost':0.18,'SARIMAX':13.66,'LightGBM':4.91, 'Hybrid':None},
#     'WATA.N0000': {'XGBoost':0.56,'SARIMAX':14.43,'LightGBM':None, 'Hybrid':15.91},
#     'AGPL.N0000': {'XGBoost':0.30,'SARIMAX':21.80,'LightGBM':10.00,'Hybrid':None},
#     'HAPU.N0000': {'XGBoost':0.25,'SARIMAX':12.43,'LightGBM':1.58, 'Hybrid':None},
#     'KOTA.N0000': {'XGBoost':0.22,'SARIMAX':7.08, 'LightGBM':1.17, 'Hybrid':None},
#     'BFL.N0000':  {'XGBoost':0.64,'SARIMAX':16.31,'LightGBM':None, 'Hybrid':10.10},
#     'RWSL.N0000': {'XGBoost':1.82,'SARIMAX':29.73,'LightGBM':None, 'Hybrid':31.14},
#     'DIPP.N0000': {'XGBoost':0.24,'SARIMAX':11.48,'LightGBM':5.52, 'Hybrid':None},
#     'MGT.N0000':  {'XGBoost':0.18,'SARIMAX':21.99,'LightGBM':0.64, 'Hybrid':None},
#     'HEXP.N0000': {'XGBoost':0.42,'SARIMAX':16.48,'LightGBM':4.85, 'Hybrid':None},
# }

# SPLIT_COMPANIES = {
#     'WATA.N0000': {'date':'2025-03-03','ratio':5,'adjusted':True},
#     'BFL.N0000':  {'date':'2023-08-01','ratio':5,'adjusted':True},
# }

# company_data = {
#     'MCPL.N0000': {'name':'Mahaweli Coconut Plantations PLC','symbol':'MCPL','sector':'Plantations',    'default_price':50.50, 'color':'#0ea5e9'},
#     'WATA.N0000': {'name':'Watawala Plantations PLC',        'symbol':'WATA','sector':'Plantations',    'default_price':180.00,'color':'#10b981'},
#     'AGPL.N0000': {'name':'Agarapatana Plantations PLC',     'symbol':'AGPL','sector':'Plantations',    'default_price':22.00, 'color':'#14b8a6'},
#     'HAPU.N0000': {'name':'Hapugastenne Plantations PLC',    'symbol':'HAPU','sector':'Plantations',    'default_price':74.00, 'color':'#06b6d4'},
#     'KOTA.N0000': {'name':'Kotagala Plantations PLC',        'symbol':'KOTA','sector':'Plantations',    'default_price':9.80,  'color':'#3b82f6'},
#     'BFL.N0000':  {'name':'Bairaha Farms PLC',               'symbol':'BFL', 'sector':'Food & Beverage','default_price':300.00,'color':'#6366f1'},
#     'RWSL.N0000': {'name':'Raigam Wayamba Salterns PLC',     'symbol':'RWSL','sector':'Manufacturing',  'default_price':27.50, 'color':'#8b5cf6'},
#     'DIPP.N0000': {'name':'Dipped Products PLC',             'symbol':'DIPP','sector':'Manufacturing',  'default_price':68.00, 'color':'#a855f7'},
#     'MGT.N0000':  {'name':'Hayleys Fabric PLC',              'symbol':'MGT', 'sector':'Plantations',    'default_price':42.50, 'color':'#d946ef'},
#     'HEXP.N0000': {'name':'Hayleys Fibre PLC',               'symbol':'HEXP','sector':'Export & Trading','default_price':95.00,'color':'#ec4899'},
# }

# # ===============================
# # MODEL LOADING
# # ===============================

# @st.cache_resource
# def load_all_models():
#     models = {k: {} for k in ['sentiment','xgboost','sarimax','lightgbm','hybrid',
#                                 'xgboost_scalers','lightgbm_scalers','hybrid_scalers',
#                                 'xgboost_features','lightgbm_features','hybrid_weights','metadata']}
#     status = {k: {} for k in ['sentiment','xgboost','sarimax','lightgbm','hybrid']}

#     # Check if model directories exist
#     if not os.path.exists(SENTIMENT_MODEL_PATH):
#         st.warning(f"⚠️ Sentiment model path not found: {SENTIMENT_MODEL_PATH}")
    
#     if not os.path.exists(PRICE_MODEL_PATH):
#         st.warning(f"⚠️ Price model path not found: {PRICE_MODEL_PATH}")

#     # Sentiment
#     for company in companies:
#         mf = f"{SENTIMENT_MODEL_PATH}/{company}_svm.joblib"
#         if os.path.exists(mf):
#             try:
#                 models['sentiment'][company] = joblib.load(mf)
#                 status['sentiment'][company] = {'loaded':True,'error':None}
#             except Exception as e:
#                 models['sentiment'][company] = None
#                 status['sentiment'][company] = {'loaded':False,'error':str(e)}
#         else:
#             models['sentiment'][company] = None
#             status['sentiment'][company] = {'loaded':False,'error':'Not found'}

#     for company in companies:
#         cd = f"{PRICE_MODEL_PATH}/{company}"
#         if not os.path.exists(cd): continue

#         # XGBoost
#         xf = f"{cd}/xgboost.joblib"
#         if os.path.exists(xf):
#             try:
#                 models['xgboost'][company] = joblib.load(xf)
#                 sf = f"{cd}/xgboost_scaler.joblib"
#                 if os.path.exists(sf): models['xgboost_scalers'][company] = joblib.load(sf)
#                 mf2 = f"{cd}/xgboost_metadata.json"
#                 if os.path.exists(mf2):
#                     with open(mf2) as f:
#                         md = json.load(f)
#                         models['metadata'][f"{company}_xgb"] = md
#                         models['xgboost_features'][company] = md.get('feature_cols',[])
#                 status['xgboost'][company] = {'loaded':True,'error':None}
#             except Exception as e:
#                 models['xgboost'][company] = None
#                 status['xgboost'][company] = {'loaded':False,'error':str(e)}
#         else:
#             models['xgboost'][company] = None
#             status['xgboost'][company] = {'loaded':False,'error':'Not found'}

#         # SARIMAX
#         sf2 = f"{cd}/sarimax.joblib"
#         if os.path.exists(sf2):
#             try:
#                 models['sarimax'][company] = joblib.load(sf2)
#                 mf3 = f"{cd}/sarimax_metadata.json"
#                 if os.path.exists(mf3):
#                     with open(mf3) as f: models['metadata'][f"{company}_sar"] = json.load(f)
#                 status['sarimax'][company] = {'loaded':True,'error':None}
#             except Exception as e:
#                 models['sarimax'][company] = None
#                 status['sarimax'][company] = {'loaded':False,'error':str(e)}
#         else:
#             models['sarimax'][company] = None
#             status['sarimax'][company] = {'loaded':False,'error':'Not found'}

#         # LightGBM
#         lf = f"{cd}/lightgbm.joblib"
#         if os.path.exists(lf):
#             try:
#                 models['lightgbm'][company] = joblib.load(lf)
#                 slgb = f"{cd}/lightgbm_scaler.joblib"
#                 if os.path.exists(slgb): models['lightgbm_scalers'][company] = joblib.load(slgb)
#                 mf4 = f"{cd}/lightgbm_metadata.json"
#                 if os.path.exists(mf4):
#                     with open(mf4) as f:
#                         md = json.load(f)
#                         models['metadata'][f"{company}_lgb"] = md
#                         models['lightgbm_features'][company] = md.get('feature_cols',[])
#                 status['lightgbm'][company] = {'loaded':True,'error':None}
#             except Exception as e:
#                 models['lightgbm'][company] = None
#                 status['lightgbm'][company] = {'loaded':False,'error':str(e)}
#         else:
#             models['lightgbm'][company] = None
#             status['lightgbm'][company] = {'loaded':False,'error':'Not found'}

#         # Hybrid
#         hwf = f"{cd}/hybrid_weights.json"
#         if os.path.exists(hwf):
#             try:
#                 with open(hwf) as f: models['hybrid_weights'][company] = json.load(f)
#                 hm = {}
#                 for mn in ['XGBoost_Robust','XGBoost_Standard','LightGBM','RandomForest']:
#                     hmf = f"{cd}/hybrid_{mn}.joblib"
#                     if os.path.exists(hmf): hm[mn] = joblib.load(hmf)
#                 hs = {}
#                 for sn in ['robust','standard']:
#                     hsf = f"{cd}/hybrid_scaler_{sn}.joblib"
#                     if os.path.exists(hsf): hs[sn] = joblib.load(hsf)
#                 if hm:
#                     models['hybrid'][company] = hm
#                     models['hybrid_scalers'][company] = hs
#                     mhf = f"{cd}/hybrid_metadata.json"
#                     if os.path.exists(mhf):
#                         with open(mhf) as f: models['metadata'][f"{company}_hybrid"] = json.load(f)
#                     status['hybrid'][company] = {'loaded':True,'error':None}
#                 else:
#                     status['hybrid'][company] = {'loaded':False,'error':'No models found'}
#             except Exception as e:
#                 models['hybrid'][company] = None
#                 status['hybrid'][company] = {'loaded':False,'error':str(e)}
#         else:
#             models['hybrid'][company] = None
#             status['hybrid'][company] = {'loaded':False,'error':'No weights'}

#     return models, status

# models, model_status = load_all_models()

# # ===============================
# # FEATURE ENGINEERING
# # ===============================

# def create_enhanced_features(company, sentiment_score, prev_close, date):
#     f = {}
#     f['price_lag1']=prev_close; f['price_lag2']=prev_close*0.99
#     f['price_lag3']=prev_close*0.98; f['price_lag5']=prev_close*0.97
#     f['price_lag10']=prev_close*0.95; f['price_lag20']=prev_close*0.90
#     er = sentiment_score*0.01
#     for k,v in [('return_1d',er),('return_2d',er*2),('return_3d',er*3),
#                 ('return_5d',er*5),('return_10d',er*10),('return_20d',er*20)]: f[k]=v
#     f['ma_3']=prev_close*(1+er*1.5); f['ma_5']=prev_close*(1+er*2)
#     f['ma_10']=prev_close*(1+er*3); f['ma_20']=prev_close*(1+er*4); f['ma_50']=prev_close*(1+er*5)
#     f['ema_5']=prev_close*(1+er*1.8); f['ema_10']=prev_close*(1+er*2.5); f['ema_20']=prev_close*(1+er*3.2)
#     f['volatility_3']=0.015+abs(sentiment_score)*0.01
#     f['volatility_5']=0.020+abs(sentiment_score)*0.01
#     f['volatility_10']=0.025+abs(sentiment_score)*0.01
#     f['volatility_20']=0.030+abs(sentiment_score)*0.01
#     f['price_vs_ma5']=prev_close/f['ma_5']-1; f['price_vs_ma10']=prev_close/f['ma_10']-1
#     f['price_vs_ma20']=prev_close/f['ma_20']-1; f['price_vs_ma50']=prev_close/f['ma_50']-1
#     f['price_vs_ema5']=prev_close/f['ema_5']-1; f['price_vs_ema10']=prev_close/f['ema_10']-1
#     f['price_vs_ema20']=prev_close/f['ema_20']-1
#     f['macd_line']=f['ema_10']-f['ema_20']; f['signal_line']=f['macd_line']*0.9
#     f['macd_histogram']=f['macd_line']-f['signal_line']
#     f['rsi']=50+(sentiment_score*30)
#     f['bb_middle']=f['ma_20']; f['bb_std']=prev_close*0.02
#     f['bb_upper']=f['bb_middle']+2*f['bb_std']; f['bb_lower']=f['bb_middle']-2*f['bb_std']
#     f['bb_position']=(prev_close-f['bb_lower'])/(f['bb_upper']-f['bb_lower']+0.001)
#     f['sentiment_raw']=sentiment_score; f['sentiment_lag1']=sentiment_score*0.95
#     f['sentiment_lag2']=sentiment_score*0.90; f['sentiment_lag3']=sentiment_score*0.85
#     f['sentiment_ma3']=sentiment_score; f['sentiment_ma5']=sentiment_score; f['sentiment_ma10']=sentiment_score
#     f['sentiment_change_1d']=0; f['sentiment_change_3d']=0; f['sentiment_change_5d']=0
#     f['sentiment_volatility_3']=abs(sentiment_score)*0.1; f['sentiment_volatility_5']=abs(sentiment_score)*0.15
#     f['price_momentum_3']=er*3; f['price_momentum_5']=er*5; f['price_momentum_10']=er*10
#     f['sentiment_price_interaction']=sentiment_score*er
#     f['sentiment_volatility_interaction']=sentiment_score*f['volatility_5']
#     f['day_of_week']=date.weekday(); f['month']=date.month
#     f['quarter']=(date.month-1)//3+1; f['day_of_month']=date.day
#     f['rolling_max_5']=prev_close*1.05; f['rolling_min_5']=prev_close*0.95
#     f['rolling_max_20']=prev_close*1.10; f['rolling_min_20']=prev_close*0.90
#     return f

# def _vec(fd, cols):
#     return np.array([fd.get(c,0) for c in cols], dtype=np.float32).reshape(1,-1)

# def prep_xgb(company,ss,pc,date,fc):  return _vec(create_enhanced_features(company,ss,pc,date), fc)
# def prep_lgb(company,ss,pc,date,fc):  return _vec(create_enhanced_features(company,ss,pc,date), fc)
# def prep_hyb(company,ss,pc,date,_='robust'):
#     fd = create_enhanced_features(company,ss,pc,date)
#     return np.array(list(fd.values()),dtype=np.float32).reshape(1,-1)
# def prep_sar(company,ss,pc,date):     return np.array([[ss]],dtype=np.float32)

# # ===============================
# # PREDICTION
# # ===============================

# def predict_xgboost(company,ss,pc,date):
#     try:
#         if not models['xgboost'].get(company): return None,0
#         fc = models['xgboost_features'].get(company,[])
#         if not fc: return None,0
#         X = prep_xgb(company,ss,pc,date,fc)
#         sc = models['xgboost_scalers'].get(company)
#         if sc: X = sc.transform(X)
#         pred = float(models['xgboost'][company].predict(X)[0])
#         mape = MODEL_METRICS[company]['XGBoost']
#         return pred, max(0.5,min(0.95,1-mape/100))
#     except: return None,0

# def predict_sarimax(company,ss,pc,date):
#     try:
#         if not models['sarimax'].get(company): return None,0
#         exog = prep_sar(company,ss,pc,date)
#         try:    pred = float(models['sarimax'][company].forecast(steps=1,exog=exog)[0])
#         except:
#             try: pred = float(models['sarimax'][company].forecast(steps=1)[0])
#             except: return None,0
#         mape = MODEL_METRICS[company]['SARIMAX']
#         return pred, max(0.5,min(0.95,1-mape/100))
#     except: return None,0

# def predict_lightgbm(company,ss,pc,date):
#     try:
#         if not models['lightgbm'].get(company): return None,0
#         fc = models['lightgbm_features'].get(company,[])
#         if not fc: return None,0
#         X = prep_lgb(company,ss,pc,date,fc)
#         sc = models['lightgbm_scalers'].get(company)
#         if sc: X = sc.transform(X)
#         pred = float(models['lightgbm'][company].predict(X)[0])
#         mape = MODEL_METRICS[company]['LightGBM']
#         conf = max(0.5,min(0.95,1-mape/100)) if mape else 0.7
#         return pred,conf
#     except: return None,0

# def predict_hybrid(company,ss,pc,date):
#     try:
#         if not models['hybrid'].get(company): return None,0
#         hm = models['hybrid'][company]; wt = models['hybrid_weights'].get(company,{})
#         sc = models['hybrid_scalers'].get(company,{})
#         Xr = prep_hyb(company,ss,pc,date,'robust')
#         Xs = prep_hyb(company,ss,pc,date,'standard')
#         if 'robust'   in sc: Xr = sc['robust'].transform(Xr)
#         if 'standard' in sc: Xs = sc['standard'].transform(Xs)
#         preds,names=[],[]
#         for mn,X in [('XGBoost_Robust',Xr),('XGBoost_Standard',Xs),('LightGBM',Xr),('RandomForest',Xr)]:
#             if mn in hm: preds.append(float(hm[mn].predict(X)[0])); names.append(mn)
#         if not preds: return None,0
#         tw = sum(wt.get(n,1/len(names)) for n in names)
#         ep = sum(preds[i]*wt.get(names[i],1/len(names)) for i in range(len(names)))
#         if tw>0: ep/=tw
#         mape = MODEL_METRICS[company].get('Hybrid',10)
#         conf = max(0.5,min(0.95,1-mape/100)) if mape else 0.7
#         return ep,conf
#     except: return None,0

# def predict_best(company,ss,pc,date):
#     bm = BEST_MODELS.get(company,'XGBoost')
#     fn_map = {'XGBoost':predict_xgboost,'SARIMAX':predict_sarimax,
#               'LightGBM':predict_lightgbm,'Hybrid':predict_hybrid}
#     fn  = fn_map.get(bm, predict_xgboost)
#     pred,conf = fn(company,ss,pc,date)
#     if pred is not None:
#         mape = MODEL_METRICS[company].get(bm)
#         lbl  = f"{bm} (MAPE: {mape:.2f}%)" if mape else bm
#         return pred,conf,lbl
#     pred,conf = predict_xgboost(company,ss,pc,date)
#     if pred is not None:
#         return pred,conf,f"XGBoost Fallback (MAPE: {MODEL_METRICS[company]['XGBoost']:.2f}%)"
#     return None,0,"No Model"

# # ===============================
# # SENTIMENT ANALYSIS
# # ===============================

# def analyze_sentiment(text, company):
#     if models['sentiment'].get(company):
#         try: return models['sentiment'][company].predict([text])[0]
#         except: pass
#     tl = text.lower()
#     pos = ['profit','growth','increase','success','positive','strong','gain','rise',
#            'ලාභ','වර්ධනය','ඉහළ','සාර්ථක','දියුණු','ජය','ඉහල','වැඩි','වාසි',
#            'dividend','bonus','expansion','record','high','up','good']
#     neg = ['loss','decline','decrease','problem','negative','weak','fall','down',
#            'අලාභ','අඩු','පහත','අසාර්ථක','ප්‍රශ්නය','අවාසි','පහල','බිඳවැටීම',
#            'crisis','risk','warning','low','bad','poor']
#     p = sum(1 for w in pos if w in tl)
#     n = sum(1 for w in neg if w in tl)
#     return "Positive" if p>n else "Negative" if n>p else "Neutral"

# # ===============================
# # SIDEBAR
# # ===============================

# with st.sidebar:
#     st.markdown("""
#     <div style='text-align:center;padding:1.2rem 0 0.6rem;'>
#         <div style='font-size:1.7rem;'>📰</div>
#         <div style='font-size:0.97rem;font-weight:700;color:#e6ecf5;margin-top:4px;'>
#             SeNtItRaDe
#         </div>
#         <div style='font-size:0.72rem;color:#4d637f;margin-top:3px;'>v3.0 · Enhanced Models</div>
#     </div>
#     """, unsafe_allow_html=True)
#     st.markdown("---")

#     # ── Language Toggle ──────────────────────────────
#     lbl_lang = t("භාෂාව", "Language")
#     st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:#4d637f;"
#                 f"letter-spacing:0.09em;text-transform:uppercase;margin-bottom:7px;'>{lbl_lang}</div>",
#                 unsafe_allow_html=True)
#     la, lb = st.columns(2)
#     with la:
#         if st.button("🇱🇰 සිංහල", use_container_width=True,
#                      type="primary" if st.session_state.lang=="si" else "secondary"):
#             st.session_state.lang = "si"; st.rerun()
#     with lb:
#         if st.button("🇬🇧 English", use_container_width=True,
#                      type="primary" if st.session_state.lang=="en" else "secondary"):
#             st.session_state.lang = "en"; st.rerun()
#     st.markdown("---")

#     # ── System Status ──
#     st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:#4d637f;"
#                 f"letter-spacing:0.09em;text-transform:uppercase;margin-bottom:8px;'>"
#                 f"{t('පද්ධති තත්ත්වය','System Status')}</div>", unsafe_allow_html=True)

#     sl = sum(1 for s in model_status['sentiment'].values() if s.get('loaded'))
#     xl = sum(1 for s in model_status['xgboost'].values()   if s.get('loaded'))
#     rl = sum(1 for s in model_status['sarimax'].values()   if s.get('loaded'))
#     ll = sum(1 for s in model_status['lightgbm'].values()  if s.get('loaded'))
#     hl = sum(1 for s in model_status['hybrid'].values()    if s.get('loaded'))

#     for label, loaded, total in [("Sentiment",sl,10),("XGBoost",xl,10),
#                                    ("SARIMAX",rl,10),("LightGBM",ll,10),("Hybrid",hl,3)]:
#         dc = "dot-on" if loaded>0 else "dot-off"
#         st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;'
#                     f'padding:3px 0;">'
#                     f'<span><span class="dot {dc}"></span>'
#                     f'<span style="color:#8fa5c2;font-size:0.83rem;font-weight:500;">{label}</span></span>'
#                     f'<span style="color:#4d637f;font-size:0.78rem;">{loaded}/{total}</span>'
#                     f'</div>', unsafe_allow_html=True)
#     st.markdown("---")

#     # ── Best Models ──
#     st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:#4d637f;"
#                 f"letter-spacing:0.09em;text-transform:uppercase;margin-bottom:8px;'>"
#                 f"{t('හොඳම ආදර්ශ','Best Models')}</div>", unsafe_allow_html=True)
#     bm_rows = []
#     for c in companies:
#         bm  = BEST_MODELS[c]
#         mpe = MODEL_METRICS[c].get(bm) or 0
#         bm_rows.append({"Symbol":company_data[c]['symbol'],"Model":bm,"MAPE":f"{mpe:.2f}%"})
#     st.dataframe(pd.DataFrame(bm_rows), hide_index=True, use_container_width=True)
#     st.markdown("---")

#     # ── Stock Splits ──
#     st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:#4d637f;"
#                 f"letter-spacing:0.09em;text-transform:uppercase;margin-bottom:8px;'>"
#                 f"{t('කොටස් බෙදීම','Stock Splits')}</div>", unsafe_allow_html=True)
#     st.dataframe(pd.DataFrame([
#         {"Co":"WATA","Date":"2025-03-03","Ratio":"1:5"},
#         {"Co":"BFL", "Date":"2023-08-01","Ratio":"1:5"},
#     ]), hide_index=True, use_container_width=True)
#     st.markdown("---")

#     # ── Config ──
#     st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:#4d637f;"
#                 f"letter-spacing:0.09em;text-transform:uppercase;margin-bottom:8px;'>"
#                 f"{t('සැකසුම්','Configuration')}</div>", unsafe_allow_html=True)
#     analysis_date = st.date_input(t("📅 විශ්ලේෂණ දිනය","📅 Analysis Date"), value=datetime.now())
#     confidence_threshold = st.slider(
#         t("🎯 විශ්වාස සීමාව","🎯 Confidence Threshold"),
#         min_value=0.0, max_value=1.0, value=0.7, step=0.05
#     )
#     st.markdown("---")

#     with st.expander(t("📋 ආදර්ශ තොරතුරු","📋 Model Info")):
#         am = np.mean([MODEL_METRICS[c][BEST_MODELS[c]] for c in companies
#                       if MODEL_METRICS[c][BEST_MODELS[c]] is not None])
#         st.markdown(f"""
#         **Version:** v3 Enhanced &nbsp;|&nbsp; **Avg MAPE:** {am:.2f}%  
#         **XGBoost:** {xl}/10 &nbsp;|&nbsp; **SARIMAX:** {rl}/10  
#         **LightGBM:** {ll}/10 &nbsp;|&nbsp; **Hybrid:** {hl}/3  
#         **{t('ආවරණය','Coverage')}:** 10 {t('සමාගම','Companies')}  
#         **{t('කොටස් බෙදීම','Splits')}:** Auto-adjusted
#         """)
#     st.markdown("---")

#     st.markdown("""
#     <div style='background:#152135;border:1px solid #223048;border-radius:12px;padding:0.9rem;'>
#         <div style='font-weight:700;color:#e6ecf5;font-size:0.88rem;'>Huzaifa Ameer</div>
#         <div style='color:#4d637f;font-size:0.75rem;margin:2px 0 5px;'>AI/ML Engineer</div>
#         <a href='https://www.linkedin.com/in/huzaifaameer/' target='_blank'
#            style='color:#6473f3;font-size:0.75rem;text-decoration:none;font-weight:600;'>🔗 LinkedIn</a>
#         <div style='color:#4d637f;font-size:0.7rem;margin-top:6px;'>© 2026 All Rights Reserved</div>
#     </div>
#     """, unsafe_allow_html=True)

# # ===============================
# # MAIN CONTENT
# # ===============================

# avg_mape = np.mean([MODEL_METRICS[c][BEST_MODELS[c]] for c in companies
#                     if MODEL_METRICS[c][BEST_MODELS[c]] is not None])

# # ── HERO ─────────────────────────────────────────────────────────────────────
# st.markdown(f"""
# <div class="hero">
#     <div class="hero-badge">📰 &nbsp; CSE · Colombo Stock Exchange · AI-Powered</div>
#     <h1 class="hero-title">
#         {t('<span>සිංහල</span> SentiTrade', '<span>Sinhala</span> SentiTrade')}
#     </h1>
#     <p class="hero-sub">
#         {t(
#             f'සිංහල ව්‍යාපාරික පුවත් හා AI ආදර්ශ ඒකාබද්ධ කර කොළඹ කොටස් හුවමාරුවේ සමාගම් 10ක '
#             f'කොටස් මිල පූර්වාවලෝකනය කරයි. XGBoost සාමාන්‍ය MAPE <strong style="color:#a5b4fc">{avg_mape:.2f}%</strong> ලබා ගනී.',
#             f'Combines Sinhala news sentiment with AI models to forecast stock prices for 10 CSE-listed companies. '
#             f'XGBoost achieves avg MAPE <strong style="color:#a5b4fc">{avg_mape:.2f}%</strong>.'
#         )}
#     </p>
#     <div class="hero-meta">
#         Developed by <a href="https://www.linkedin.com/in/huzaifaameer/" target="_blank">Huzaifa Ameer</a> © 2026
#     </div>
# </div>
# """, unsafe_allow_html=True)

# # ── SYSTEM DESCRIPTION ───────────────────────────────────────────────────────
# st.markdown(f"""
# <div class="sys-card">
#     <h3>🚀 {t('පද්ධතිය ගැන', 'About This System')}</h3>
#     <p>
#         {t(
#             '<strong>සිංහල News Sentinel v3</strong> යනු XGBoost, LightGBM, SARIMAX හා Hybrid ආදර්ශ '
#             'භාවිතා කරමින් කොළඹ කොටස් හුවමාරුවේ (CSE) ලැයිස්තුගත සමාගම් 10ක කොටස් '
#             'මිල ප්‍රශස්ත නිරවද්‍යතාවයෙන් පූර්වාවලෝකනය කරන AI-ශක්තිමත් පද්ධතියකි. '
#             'සිංහල ව්‍යාපාරික පුවත් වල සංවේදනා (sentiment) පදනම් කරගෙන මිල ගැනීම් කරනු ලැබේ.',
#             '<strong>SentiTrade v3</strong> is an AI-powered stock price forecasting system '
#             'for 10 CSE-listed companies, using XGBoost, LightGBM, SARIMAX and Hybrid ensemble models. '
#             'Sentiment extracted from Sinhala business news drives each prediction.'
#         )}
#     </p>
#     <hr class="sys-divider">
#     <p><strong style="color:#a5b4fc;">
#         📥 {t('ඔබ ඇතුළත් කළ යුතු දේ', 'Required Inputs')}
#     </strong></p>
#     <ul>
#         <li>
#             📰&nbsp;<strong>{t('සිංහල ව්‍යාපාරික පුවත් ලිපි', 'Sinhala business news articles')}</strong>
#             {t(
#                 ' — <strong>සිංහල භාෂාවෙන් පමණයි.</strong> ලිපි කිහිපයක් ඇතුළත් කළ හොත් '
#                 'සංවේදනා ලකුණ වඩාත් නිවැරදි වේ.',
#                 ' — <strong>Sinhala language only.</strong> Adding more articles improves accuracy.'
#             )}
#         </li>
#         <li>
#             💰&nbsp;<strong>{t('ඊයේ වසා දැමූ කොටස් මිල', "Yesterday's closing stock price")}</strong>
#             {t(' — රුපියල් (Rs.) ඒකකයෙන් ඇතුළත් කරන්න.', ' — Enter in Rupees (Rs.).')}
#         </li>
#         <li>
#             📅&nbsp;<strong>{t('විශ්ලේෂණ දිනය', 'Analysis date')}</strong>
#             {t(' — Sidebar එකෙන් දිනය තෝරන්න.', ' — Choose from the sidebar.')}
#         </li>
#     </ul>
#     <hr class="sys-divider">
#     <p style="margin:0;font-size:0.83rem;color:#f5b731;">
#         ⚠️&nbsp;{t(
#             '<strong>වැදගත්:</strong> සංවේදනා ආදර්ශය සිංහල ව්‍යාපාරික පුවත් සඳහා පමණක් '
#             'ප්‍රශස්ත ලෙස පුහුණු කර ඇත. ඉංග්‍රීසි හෝ වෙනත් භාෂා ලිපි ඇතුළත් කිරීමෙන් '
#             'ප්‍රතිඵල නිරවද්‍ය නොවිය හැක.',
#             '<strong>Important:</strong> The sentiment model is optimised exclusively for Sinhala '
#             'business news. Using English or other language text may reduce accuracy.'
#         )}
#     </p>
# </div>
# """, unsafe_allow_html=True)

# # ── INPUT TABS ────────────────────────────────────────────────────────────────
# st.markdown(f'<div class="sec-hdr"><span class="sec-dot"></span>📝 '
#             f'{t("දත්ත ඇතුළත් කිරීම","Data Input")}</div>', unsafe_allow_html=True)

# tab1, tab2 = st.tabs([
#     f"📰 {t('සිංහල පුවත් ලිපි','Sinhala News Articles')}",
#     f"💰 {t('කොටස් මිල','Stock Prices')}"
# ])

# with tab1:
#     st.markdown(f"""
#     <div class='info-box'>
#         <strong>📌 {t('උපදෙස','Tip')}:</strong>&nbsp;
#         {t(
#             'සිංහල ව්‍යාපාරික පුවත් ලිපි පමණක් ඇතුළත් කරන්න. '
#             'ලිපි ගණන වැඩිවන තරමට විශ්ලේෂණය නිවැරදිය.',
#             'Enter Sinhala business news articles only. '
#             'More articles = more reliable predictions.'
#         )}&nbsp;
#         <span style="color:#f5b731;font-weight:600;">
#             🔒 {t('සිංහල ව්‍යාපාරික ලිපි පමණයි · Sinhala articles only','Sinhala articles only')}
#         </span>
#     </div>
#     """, unsafe_allow_html=True)

#     if "news_inputs" not in st.session_state:
#         st.session_state.news_inputs = [""]

#     ca, cb, cc = st.columns([3,1,1])
#     with cb:
#         if st.button(f"➕ {t('ලිපිය එකතු කරන්න','Add Article')}", use_container_width=True):
#             st.session_state.news_inputs.append(""); st.rerun()
#     with cc:
#         if st.button(f"🗑️ {t('සියල්ල මකන්න','Clear All')}", use_container_width=True):
#             st.session_state.news_inputs = [""]; st.rerun()

#     news_texts = []
#     for i in range(len(st.session_state.news_inputs)):
#         news = st.text_area(
#             f"{t('ලිපිය','Article')} {i+1}",
#             height=130,
#             value=st.session_state.news_inputs[i],
#             key=f"news_{i}",
#             placeholder=t(
#                 "සිංහල ව්‍යාපාරික පුවත් ලිපිය මෙහි අලවන්න... "
#                 "(උදා: 'ලංකා IOC හි ලාභය රු. මිලියන 450 දක්වා ඉහළ ගොස් ඇත.')",
#                 "Paste your Sinhala business news article here... "
#                 "(e.g.: 'Lanka IOC profits rise to Rs. 450 million.')"
#             )
#         )
#         news_texts.append(news)
#         st.session_state.news_inputs[i] = news

# with tab2:
#     st.markdown(f"""
#     <div class='info-box'>
#         <strong>💡 {t('සටහන','Note')}:</strong>&nbsp;
#         {t(
#             'ඊයේ දිනයේ (Previous Closing Price) කොටස් මිල රුපියල් (Rs.) ඒකකයෙන් '
#             'ඇතුළත් කරන්න. WATA හා BFL — කොටස් බෙදීම ස්වයංක්‍රීයව ගළපා ඇත.',
#             "Enter yesterday's closing prices in Rupees (Rs.). "
#             'WATA and BFL stock splits are automatically adjusted.'
#         )}
#     </div>
#     """, unsafe_allow_html=True)

#     prev_close_prices = {}
#     sectors = {}
#     for c in companies:
#         sectors.setdefault(company_data[c]['sector'],[]).append(c)

#     for sector, sector_cos in sectors.items():
#         with st.expander(f"📊 {sector}", expanded=True):
#             cols = st.columns(min(3, len(sector_cos)))
#             for idx, c in enumerate(sector_cos):
#                 with cols[idx % 3]:
#                     info = company_data[c]
#                     if c in SPLIT_COMPANIES:
#                         st.markdown(
#                             f"**{info['symbol']}** "
#                             f"<span style='color:#f5b731;font-size:0.68rem;'>"
#                             f"({t('බෙදීම-ගළපනලදී','split-adj')})</span>",
#                             unsafe_allow_html=True)
#                     else:
#                         st.markdown(f"**{info['symbol']}**")
#                     st.caption(info['name'][:28]+"...")
#                     prev_close_prices[c] = st.number_input(
#                         t("මිල (රු.)","Price (Rs.)"),
#                         min_value=0.0, value=info['default_price'],
#                         step=0.1, format="%.2f", key=f"price_{c}"
#                     )

# # ── ANALYSE BUTTON ────────────────────────────────────────────────────────────
# st.markdown("---")
# _, btn_col, _ = st.columns([1,2,1])
# with btn_col:
#     analyze_button = st.button(
#         f"🚀 {t('දියුණු ආදර්ශ සමඟ විශ්ලේෂණය කරන්න','Run Analysis with Enhanced Models')}",
#         type="primary", use_container_width=True
#     )

# # ===============================
# # ANALYSIS EXECUTION
# # ===============================

# if analyze_button:
#     if all(tx.strip()=="" for tx in news_texts):
#         st.warning(t("⚠️ විශ්ලේෂණය සඳහා අවම වශයෙන් එක් සිංහල පුවත් ලිපියක් ඇතුළත් කරන්න.",
#                      "⚠️ Please enter at least one Sinhala news article."))
#         st.stop()

#     pb = st.progress(0)
#     st_txt = st.empty()

#     # ── Sentiment ──
#     st_txt.text(t("🔍 සිංහල ලිපිවල සංවේදනා විශ්ලේෂණය කරමින්...",
#                   "🔍 Analysing sentiment in Sinhala articles..."))
#     sent_res = []
#     for idx, text in enumerate(news_texts,1):
#         if text.strip()=="": continue
#         row = {t("ලිපිය","Article"):f"{t('ලිපිය','Article')} {idx}",
#                t("පෙරදසුන","Preview"):text[:100]+"..."}
#         for c in companies: row[c] = analyze_sentiment(text,c)
#         sent_res.append(row)
#         pb.progress((idx/len(news_texts))*0.4)

#     sentiment_df = pd.DataFrame(sent_res)
#     smap = {"Positive":1,"Neutral":0,"Negative":-1}
#     score_mx = sentiment_df[[c for c in companies if c in sentiment_df.columns]].copy()
#     for c in companies:
#         if c in score_mx.columns: score_mx[c] = score_mx[c].map(smap)
#     daily_scores = score_mx.mean().reset_index()
#     daily_scores.columns = ["Company","Average_Sentiment_Score"]

#     # ── Price Predictions ──
#     st_txt.text(t("💰 දියුණු ආදර්ශ භාවිතා කර මිල පූර්වාවලෝකනය...",
#                   "💰 Generating price predictions with enhanced models..."))
#     preds_list, failed = [], []
#     for idx,(_, row_d) in enumerate(daily_scores.iterrows()):
#         company = row_d["Company"]; ss = row_d["Average_Sentiment_Score"]
#         pc = prev_close_prices.get(company, company_data[company]['default_price'])
#         pred_price, conf, model_used = predict_best(company,ss,pc,analysis_date)
#         if pred_price is None: failed.append(company_data[company]['symbol']); continue
#         chg_amt = pred_price-pc; chg_pct = (chg_amt/pc)*100
#         bm = BEST_MODELS[company]; bm_mape = MODEL_METRICS[company].get(bm) or 0
#         preds_list.append({
#             "Company":company_data[company]['name'],
#             "Symbol":company_data[company]['symbol'],
#             "Sector":company_data[company]['sector'],
#             "Previous_Close":pc, "Predicted_Price":pred_price,
#             "Price_Change":chg_amt, "Price_Change_Percent":chg_pct,
#             "Sentiment_Score":ss,
#             "Sentiment_Category":"Positive" if ss>0.1 else "Negative" if ss<-0.1 else "Neutral",
#             "Model_Used":model_used,
#             "Best_MAPE":f"{bm_mape:.2f}%" if bm_mape else "N/A",
#             "Confidence":conf, "Split_Adjusted":company in SPLIT_COMPANIES,
#             "Color":company_data[company]['color']
#         })
#         pb.progress(0.4+((idx+1)/len(companies))*0.6)

#     if failed:
#         st.warning(f"⚠️ {t('පූර්වාවලෝකනය නොහැකි','Unavailable')}: {', '.join(failed)}")
#     if not preds_list:
#         st.error(t("❌ කිසිදු පූර්වාවලෝකනයක් ජනනය කළ නොහැකිය.","❌ No predictions generated."))
#         st.stop()

#     predictions_df = pd.DataFrame(preds_list)
#     pb.empty(); st_txt.empty()

#     # ── Results ──────────────────────────────────────────────────────────────
#     st.markdown(f'<div class="sec-hdr"><span class="sec-dot"></span>📊 '
#                 f'{t("විශ්ලේෂණ ප්‍රතිඵල v3","Analysis Results v3")}</div>', unsafe_allow_html=True)

#     c1,c2,c3,c4 = st.columns(4)
#     avg_ret = predictions_df['Price_Change_Percent'].mean()
#     pos_n   = len(predictions_df[predictions_df['Price_Change_Percent']>0])
#     avg_snt = predictions_df['Sentiment_Score'].mean()
#     bstp    = predictions_df.loc[predictions_df['Price_Change_Percent'].idxmax()]
#     c1.metric(t("සාමාන්‍ය ප්‍රතිලාභය","Avg Return"),       f"{avg_ret:+.2f}%")
#     c2.metric(t("ලාභ ලබා ගන්නන්","Gainers"),               f"{pos_n}/{len(preds_list)}")
#     c3.metric(t("සංවේදනා ලකුණ","Sentiment Score"),        f"{avg_snt:.3f}")
#     c4.metric(t("ඉහළම කාර්ය සාධනය","Top Performer"),      bstp['Symbol'],
#               delta=f"+{bstp['Price_Change_Percent']:.1f}%")

#     st.markdown(f"##### 🤖 {t('ආදර්ශ කාර්ය සාධනය','Model Performance')}")
#     ms = predictions_df.groupby('Model_Used').agg({'Confidence':'mean','Symbol':'count'}).round(3)
#     ms.columns = [t('සාමාන්‍ය විශ්වාසය','Avg Confidence'), t('ගණන','Count')]
#     st.dataframe(ms, use_container_width=True)

#     # Article Sentiment
#     st.markdown(f'<div class="sec-hdr"><span class="sec-dot"></span>📰 '
#                 f'{t("ලිපිවල සංවේදනා","Article Sentiment")}</div>', unsafe_allow_html=True)

#     ad = sentiment_df.copy()
#     rd = {}
#     for c in companies:
#         if c in ad.columns: rd[c] = company_data[c]['symbol']
#     ad = ad.rename(columns=rd)

#     def _sty(val):
#         if val=="Positive": return 'background-color:rgba(16,201,138,0.15);color:#10c98a;'
#         if val=="Negative": return 'background-color:rgba(240,92,110,0.15);color:#f05c6e;'
#         if val=="Neutral":  return 'background-color:rgba(100,116,139,0.15);color:#8fa5c2;'
#         return ''

#     sym_cols = [company_data[c]['symbol'] for c in companies if company_data[c]['symbol'] in ad.columns]
#     st.dataframe(ad.style.map(_sty, subset=sym_cols), use_container_width=True, height=340)

#     # Price Predictions Table
#     st.markdown(f'<div class="sec-hdr"><span class="sec-dot"></span>💰 '
#                 f'{t("මිල පූර්වාවලෝකනය","Price Predictions")}</div>', unsafe_allow_html=True)

#     disp = predictions_df.copy()
#     disp['Previous_Close']       = disp['Previous_Close'].map(lambda x: f"Rs. {x:,.2f}")
#     disp['Predicted_Price']      = disp['Predicted_Price'].map(lambda x: f"Rs. {x:,.2f}")
#     disp['Price_Change']         = disp['Price_Change'].map(lambda x: f"{x:+,.2f}")
#     disp['Price_Change_Percent'] = disp['Price_Change_Percent'].map(lambda x: f"{x:+.2f}%")
#     disp['Sentiment_Score']      = disp['Sentiment_Score'].map(lambda x: f"{x:.3f}")
#     disp['Confidence']           = disp['Confidence'].map(lambda x: f"{x:.1%}")
#     disp['Split']                = disp['Split_Adjusted'].map(lambda x: "✓" if x else "—")
#     col_rename = {
#         'Symbol':              t('සිරස','Symbol'),
#         'Sector':              t('අංශය','Sector'),
#         'Previous_Close':      t('පෙර මිල','Prev Close'),
#         'Predicted_Price':     t('පෙලෙන මිල','Predicted'),
#         'Price_Change_Percent':t('වෙනස %','Change %'),
#         'Model_Used':          t('ආදර්ශය','Model'),
#         'Best_MAPE':           'MAPE',
#         'Confidence':          t('විශ්වාසය','Conf'),
#         'Split':               t('බෙදීම','Split'),
#     }
#     st.dataframe(disp[list(col_rename.keys())].rename(columns=col_rename),
#                  use_container_width=True, height=390)

#     # Charts
#     st.markdown(f'<div class="sec-hdr"><span class="sec-dot"></span>📊 '
#                 f'{t("ප්‍රස්ථාර","Charts")}</div>', unsafe_allow_html=True)

#     vt1,vt2,vt3 = st.tabs([
#         f"📈 {t('මිල වෙනස','Price Changes')}",
#         f"🎯 {t('සංවේදනා','Sentiment')}",
#         f"🏢 {t('අංශය','Sector')}",
#     ])
#     _bg = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
#                font=dict(color='#8fa5c2'), margin=dict(l=10,r=10,t=42,b=10))

#     with vt1:
#         v1,v2 = st.columns(2)
#         with v1:
#             sdf = predictions_df.sort_values('Price_Change_Percent',ascending=True)
#             fig = go.Figure(go.Bar(
#                 x=sdf['Price_Change_Percent'], y=sdf['Symbol'], orientation='h',
#                 marker_color=['#f05c6e' if x<0 else '#10c98a' for x in sdf['Price_Change_Percent']],
#                 text=sdf['Price_Change_Percent'].map(lambda x:f"{x:+.1f}%"), textposition='outside'
#             ))
#             fig.update_layout(title=t("අපේක්ෂිත මිල වෙනස","Expected Price Changes"),
#                               xaxis_title=t("වෙනස (%)","Change (%)"),height=430,**_bg)
#             st.plotly_chart(fig,use_container_width=True)
#         with v2:
#             fig = go.Figure()
#             fig.add_trace(go.Scatter(x=predictions_df['Symbol'],y=predictions_df['Previous_Close'],
#                 mode='markers+lines',name=t('පෙර','Prev Close'),
#                 marker=dict(size=8,color='#4d637f'),line=dict(color='#4d637f',dash='dot')))
#             fig.add_trace(go.Scatter(x=predictions_df['Symbol'],y=predictions_df['Predicted_Price'],
#                 mode='markers+lines',name=t('පෙලෙන','Predicted'),
#                 marker=dict(size=11,color='#6473f3'),line=dict(color='#6473f3',width=3)))
#             fig.update_layout(title=t("මිල සන්සන්දනය","Price Comparison"),
#                               yaxis_title=t("මිල (රු.)","Price (Rs.)"),height=430,**_bg)
#             st.plotly_chart(fig,use_container_width=True)

#     with vt2:
#         v1,v2 = st.columns(2)
#         with v1:
#             fig = px.scatter(predictions_df,x='Sentiment_Score',y='Price_Change_Percent',
#                 size='Previous_Close',color='Sector',text='Symbol',
#                 title=t("සංවේදනා vs මිල","Sentiment vs Price"),height=430)
#             fig.update_traces(textposition='top center')
#             fig.update_layout(**_bg)
#             st.plotly_chart(fig,use_container_width=True)
#         with v2:
#             sc = predictions_df['Sentiment_Category'].value_counts()
#             fig = go.Figure(go.Pie(labels=sc.index,values=sc.values,hole=0.42,
#                 marker=dict(colors=['#10c98a','#4d637f','#f05c6e'])))
#             fig.update_layout(title=t("සංවේදනා බෙදාහැරීම","Sentiment Distribution"),
#                               height=430,**_bg)
#             st.plotly_chart(fig,use_container_width=True)

#     with vt3:
#         v1,v2 = st.columns(2)
#         with v1:
#             sp = predictions_df.groupby('Sector')['Price_Change_Percent'].mean().reset_index()
#             fig = go.Figure(go.Bar(
#                 x=sp['Sector'],y=sp['Price_Change_Percent'],
#                 text=sp['Price_Change_Percent'].map(lambda x:f"{x:+.1f}%"),textposition='outside',
#                 marker_color=['#10c98a' if x>0 else '#f05c6e' for x in sp['Price_Change_Percent']]
#             ))
#             fig.update_layout(title=t("අංශය අනුව සාමාන්‍ය","Avg by Sector"),height=430,**_bg)
#             st.plotly_chart(fig,use_container_width=True)
#         with v2:
#             sct = predictions_df['Sector'].value_counts()
#             fig = go.Figure(go.Bar(x=sct.values,y=sct.index,orientation='h',
#                 marker_color='#6473f3',text=sct.values,textposition='outside'))
#             fig.update_layout(title=t("අංශය අනුව සමාගම් ගණන","Companies by Sector"),height=430,**_bg)
#             st.plotly_chart(fig,use_container_width=True)

#     # Recommendations
#     st.markdown(f'<div class="sec-hdr"><span class="sec-dot"></span>💡 '
#                 f'{t("නිර්දේශ","Recommendations")}</div>', unsafe_allow_html=True)

#     rc1,rc2 = st.columns(2)
#     with rc1:
#         st.markdown(f"#### 🎯 {t('ඉහළම අවස්ථා','Top Opportunities')}")
#         hc  = predictions_df[predictions_df['Confidence']>=confidence_threshold]
#         top3= hc.nlargest(3,'Price_Change_Percent')
#         if len(top3)==0:
#             st.info(t("විශ්වාස සීමාවට ගැළපෙන අවස්ථා නොමැත.","No opportunities meet the threshold."))
#         else:
#             for _,row in top3.iterrows():
#                 sn=" ("+t("බෙදීම-ගළපනලදී","Split-adj")+")" if row['Split_Adjusted'] else ""
#                 st.markdown(f"""<div class='opp-card'>
#                     <h4>{row['Symbol']} — {row['Company']}{sn}</h4>
#                     <div class='c-row'><strong>{t('ඉලක්ක','Target')}:</strong> Rs.&nbsp;{row['Predicted_Price']:.2f}
#                     &nbsp;|&nbsp; <strong>{t('ප්‍රතිලාභය','Return')}:</strong>
#                     <span class='tg'>{row['Price_Change_Percent']:+.2f}%</span></div>
#                     <div class='c-row'><strong>{t('ආදර්ශය','Model')}:</strong> {row['Model_Used']}
#                     &nbsp;|&nbsp; <strong>MAPE:</strong> {row['Best_MAPE']}
#                     &nbsp;|&nbsp; <strong>{t('විශ්වාසය','Conf')}:</strong> {row['Confidence']:.1%}</div>
#                 </div>""", unsafe_allow_html=True)

#     with rc2:
#         st.markdown(f"#### ⚠️ {t('අවධානයෙන් බලන්න','Monitor')}")
#         bot3 = predictions_df.nsmallest(3,'Price_Change_Percent')
#         for _,row in bot3.iterrows():
#             sn=" ("+t("බෙදීම-ගළපනලදී","Split-adj")+")" if row['Split_Adjusted'] else ""
#             st.markdown(f"""<div class='mon-card'>
#                 <h4>{row['Symbol']} — {row['Company']}{sn}</h4>
#                 <div class='c-row'><strong>{t('ඉලක්ක','Target')}:</strong> Rs.&nbsp;{row['Predicted_Price']:.2f}
#                 &nbsp;|&nbsp; <strong>{t('ප්‍රතිලාභය','Return')}:</strong>
#                 <span class='tr'>{row['Price_Change_Percent']:+.2f}%</span></div>
#                 <div class='c-row'><strong>{t('ආදර්ශය','Model')}:</strong> {row['Model_Used']}
#                 &nbsp;|&nbsp; <strong>MAPE:</strong> {row['Best_MAPE']}
#                 &nbsp;|&nbsp; <strong>{t('විශ්වාසය','Conf')}:</strong> {row['Confidence']:.1%}</div>
#             </div>""", unsafe_allow_html=True)

#     # Export
#     st.markdown(f'<div class="sec-hdr"><span class="sec-dot"></span>📥 '
#                 f'{t("අපනයනය","Export")}</div>', unsafe_allow_html=True)

#     e1,e2,e3 = st.columns(3)
#     with e1:
#         st.download_button(f"📊 {t('පූර්වාවලෝකන','Predictions')}",
#             predictions_df.to_csv(index=False),
#             f"predictions_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
#             "text/csv", use_container_width=True)
#     with e2:
#         st.download_button(f"📰 {t('සංවේදනා','Sentiment')}",
#             sentiment_df.to_csv(index=False),
#             f"sentiment_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
#             "text/csv", use_container_width=True)
#     with e3:
#         full = predictions_df.copy()
#         full['Analysis_Date']     = analysis_date
#         full['Articles_Analyzed'] = len([tx for tx in news_texts if tx.strip()])
#         full['Model_Version']     = 'v3_enhanced'
#         st.download_button(f"📄 {t('සම්පූර්ණ වාර්තාව','Full Report')}",
#             full.to_csv(index=False),
#             f"full_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
#             "text/csv", use_container_width=True)

#     # Disclaimer
#     st.markdown("---")
#     st.markdown(f"""
#     <div class='warn-box'>
#         <strong>⚠️ {t('වියාකරණය','Disclaimer')}</strong><br>
#         {t(
#             'මෙම විශ්ලේෂණය <code>price_models_final_v3/</code> ආදර්ශ භාවිතා කරයි. '
#             'XGBoost බොහෝ සමාගම් සඳහා 1%ට අඩු MAPE ලබා ගනී. '
#             'අතීත කාර්ය සාධනය අනාගත ප්‍රතිඵල සහතික නොකරයි. '
#             '<strong>මෙය මූල්‍ය උපදෙසක් නොවේ.</strong>',
#             'This analysis uses models from <code>price_models_final_v3/</code>. '
#             'XGBoost achieves &lt;1% MAPE for most companies. '
#             'Past performance does not guarantee future results. '
#             '<strong>Not financial advice.</strong>'
#         )}
#     </div>
#     """, unsafe_allow_html=True)

# # ── FOOTER ────────────────────────────────────────────────────────────────────
# st.markdown(f"""
# <div class='footer'>
#     <strong>📰 SentiTrade</strong><br>
#     {t('දියුණු ආදර්ශ v3 · සාමාන්‍ය MAPE: 0.48%',
#        'Enhanced Models v3 · Avg MAPE: 0.48%')}<br>
#     {t('සෑදුවේ','Developed with')} ❤️ {t('විසින්','by')}
#     <a href='https://www.linkedin.com/in/huzaifaameer/' target='_blank'>Huzaifa Ameer</a> | © 2026<br>
#     <span style='font-size:0.73rem;color:#4d637f;'>
#         Version 3.0 · Enhanced Models · XGBoost &lt;1% MAPE · Stock Split Adjusted
#     </span>
# </div>
# """, unsafe_allow_html=True)

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
from huggingface_hub import snapshot_download
import tempfile

# ===============================
# HUGGING FACE MODEL DOWNLOAD
# ===============================

@st.cache_resource(show_spinner=False)
def download_models_persistent():
    REPO_ID = "huzaifaameer/sinhala-news-sentinel"
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "sinhala-news-sentinel")
    os.makedirs(cache_dir, exist_ok=True)
    model_path = os.path.join(cache_dir, "models")
    if not os.path.exists(model_path) or not os.listdir(model_path):
        local_dir = snapshot_download(
            repo_id=REPO_ID,
            repo_type="space",
            local_dir=model_path,
            local_dir_use_symlinks=False
        )
    return model_path

_loading_placeholder = st.empty()
with _loading_placeholder.container():
    st.markdown("""
    <style>
    .load-screen {
        display:flex;flex-direction:column;align-items:center;justify-content:center;
        min-height:60vh;gap:1.2rem;
    }
    .load-spinner {
        width:44px;height:44px;border:3px solid #e2e8f0;
        border-top:3px solid #1e40af;border-radius:50%;
        animation:spin 0.9s linear infinite;
    }
    @keyframes spin{to{transform:rotate(360deg)}}
    .load-title{font-family:'DM Sans',sans-serif;font-size:1.1rem;font-weight:600;color:#1e293b;}
    .load-sub{font-family:'DM Sans',sans-serif;font-size:0.82rem;color:#64748b;}
    </style>
    <div class="load-screen">
        <div class="load-spinner"></div>
        <div class="load-title">Starting SentiTrade</div>
        <div class="load-sub">Loading intelligence models, please wait…</div>
    </div>
    """, unsafe_allow_html=True)

try:
    MODEL_CACHE_PATH = download_models_persistent()
    SENTIMENT_MODEL_PATH = os.path.join(MODEL_CACHE_PATH, "saved_models")
    PRICE_MODEL_PATH = os.path.join(MODEL_CACHE_PATH, "price_models_final_v3")
except Exception as e:
    MODEL_CACHE_PATH = "."
    SENTIMENT_MODEL_PATH = os.path.join(".", "saved_models")
    PRICE_MODEL_PATH = os.path.join(".", "price_models_final_v3")

_loading_placeholder.empty()

# ===============================
# PAGE CONFIG
# ===============================

st.set_page_config(
    page_title="SentiTrade · CSE Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# LANGUAGE HELPER
# ===============================

if "lang" not in st.session_state:
    st.session_state.lang = "si"
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "home"

def t(si_text, en_text):
    return si_text if st.session_state.lang == "si" else en_text

# ===============================
# GLOBAL STYLES
# ===============================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=Noto+Sans+Sinhala:wght@300;400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');

:root {
    --navy:      #0f172a;
    --navy-2:    #1e293b;
    --navy-3:    #273549;
    --slate:     #334155;
    --border:    #e2e8f0;
    --border-d:  #334155;
    --blue:      #1d4ed8;
    --blue-lt:   #3b82f6;
    --blue-dim:  rgba(29,78,216,0.08);
    --blue-glow: rgba(29,78,216,0.22);
    --sky:       #0ea5e9;
    --green:     #059669;
    --red:       #dc2626;
    --amber:     #d97706;
    --txt-dark:  #0f172a;
    --txt-mid:   #475569;
    --txt-light: #94a3b8;
    --bg:        #f8fafc;
    --surface:   #ffffff;
    --surface-2: #f1f5f9;
    --r:         10px;
    --rl:        16px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', 'Noto Sans Sinhala', sans-serif !important;
    background: var(--bg) !important;
    color: var(--txt-dark) !important;
    -webkit-font-smoothing: antialiased;
}
h1,h2,h3,h4,h5,h6 { font-family:'DM Sans','Noto Sans Sinhala',sans-serif; }
#MainMenu, footer, header { visibility:hidden; }

::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#f1f5f9; }
::-webkit-scrollbar-thumb { background:#cbd5e1; border-radius:3px; }

/* ── NAV ── */
.topnav {
    display:flex;align-items:center;justify-content:space-between;
    background:var(--surface);border-bottom:1px solid var(--border);
    padding:0 2rem;height:60px;position:sticky;top:0;z-index:999;
    box-shadow:0 1px 4px rgba(0,0,0,0.06);
}
.nav-brand {
    display:flex;align-items:center;gap:10px;
    font-weight:700;font-size:1.05rem;color:var(--navy);letter-spacing:-0.3px;
}
.nav-brand-dot { width:8px;height:8px;border-radius:50%;background:var(--blue);flex-shrink:0; }
.nav-links { display:flex;align-items:center;gap:4px; }
.nav-link {
    padding:6px 14px;border-radius:8px;font-size:0.84rem;font-weight:500;
    color:var(--txt-mid);cursor:pointer;transition:all 0.15s;text-decoration:none;border:none;
    background:transparent;
}
.nav-link:hover { background:var(--surface-2);color:var(--navy); }
.nav-link.active { background:var(--blue-dim);color:var(--blue);font-weight:600; }
.nav-right { display:flex;align-items:center;gap:10px; }
.nav-badge {
    font-size:0.68rem;font-weight:700;color:var(--txt-light);
    letter-spacing:0.06em;background:var(--surface-2);
    padding:3px 9px;border-radius:20px;border:1px solid var(--border);
}

/* ── PAGE WRAPPER ── */
.page-wrap { max-width:1140px;margin:0 auto;padding:2rem 1.25rem; }

/* ── HERO ── */
.hero-wrap {
    background:var(--navy);border-radius:var(--rl);
    padding:3.5rem 3rem;margin-bottom:2rem;
    position:relative;overflow:hidden;
}
.hero-wrap::before {
    content:'';position:absolute;inset:0;
    background:radial-gradient(ellipse 70% 80% at 90% 50%,
        rgba(29,78,216,0.35) 0%,transparent 65%);
    pointer-events:none;
}
.hero-wrap::after {
    content:'';position:absolute;bottom:-40px;right:-30px;
    width:220px;height:220px;border-radius:50%;
    background:rgba(14,165,233,0.08);
    pointer-events:none;
}
.hero-label {
    display:inline-flex;align-items:center;gap:7px;
    font-size:0.7rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;
    color:rgba(148,163,184,0.9);margin-bottom:1.1rem;
}
.hero-label span {
    width:5px;height:5px;border-radius:50%;background:#3b82f6;display:inline-block;
}
.hero-title {
    font-size:clamp(2rem,3.5vw,3.1rem);font-weight:700;
    color:#f1f5f9;line-height:1.12;letter-spacing:-0.8px;
    margin:0 0 0.8rem;
}
.hero-title em { font-style:normal;color:#93c5fd; }
.hero-desc {
    color:rgba(148,163,184,0.85);font-size:0.97rem;
    line-height:1.8;max-width:560px;margin:0;
}
.hero-stats {
    display:flex;gap:2rem;margin-top:2.5rem;flex-wrap:wrap;
}
.hero-stat-val {
    font-size:1.5rem;font-weight:700;color:#f1f5f9;line-height:1;
}
.hero-stat-lbl {
    font-size:0.72rem;color:rgba(148,163,184,0.7);
    margin-top:3px;letter-spacing:0.04em;
}

/* ── SECTION HEADER ── */
.sec-hdr {
    display:flex;align-items:center;gap:10px;
    margin:2.5rem 0 1.2rem;padding-bottom:0.75rem;
    border-bottom:1px solid var(--border);
}
.sec-hdr-title {
    font-size:0.75rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
    color:var(--txt-mid);
}
.sec-hdr-line { flex:1;height:1px;background:var(--border); }

/* ── CARD ── */
.card {
    background:var(--surface);border:1px solid var(--border);
    border-radius:var(--rl);padding:1.5rem;
    box-shadow:0 1px 3px rgba(0,0,0,0.04);
}
.card-accent { border-left:3px solid var(--blue); }

/* ── INFO BOX ── */
.info-box {
    background:#eff6ff;border:1px solid #bfdbfe;
    border-radius:var(--r);padding:1rem 1.2rem;
    margin:0.75rem 0;color:#1e40af;font-size:0.87rem;line-height:1.75;
}
.warn-box {
    background:#fffbeb;border:1px solid #fde68a;
    border-radius:var(--r);padding:1rem 1.2rem;
    margin:0.75rem 0;color:#92400e;font-size:0.87rem;line-height:1.75;
}
.success-box {
    background:#ecfdf5;border:1px solid #a7f3d0;
    border-radius:var(--r);padding:1rem 1.2rem;
    margin:0.75rem 0;color:#065f46;font-size:0.87rem;line-height:1.75;
}

/* ── STATUS DOTS ── */
.dot { width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:6px;vertical-align:middle; }
.dot-on  { background:#10b981; }
.dot-off { background:#ef4444; }
.dot-warn{ background:#f59e0b; }

/* ── METRIC CARDS ── */
.metric-grid { display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1rem;margin-bottom:1.5rem; }
.metric-card {
    background:var(--surface);border:1px solid var(--border);
    border-radius:var(--rl);padding:1.25rem 1.4rem;
    box-shadow:0 1px 3px rgba(0,0,0,0.04);
}
.metric-val { font-size:1.65rem;font-weight:700;color:var(--navy);line-height:1; }
.metric-lbl { font-size:0.74rem;color:var(--txt-mid);margin-top:5px;font-weight:500;letter-spacing:0.02em; }
.metric-delta-up { font-size:0.78rem;color:var(--green);font-weight:600;margin-top:3px; }
.metric-delta-dn { font-size:0.78rem;color:var(--red);font-weight:600;margin-top:3px; }

/* ── OPP / MONITOR CARDS ── */
.opp-card {
    background:#f0fdf4;border:1px solid #bbf7d0;border-radius:var(--rl);
    padding:1.2rem 1.35rem;margin-bottom:0.75rem;
}
.opp-card-title { font-size:0.92rem;font-weight:700;color:#065f46;margin:0 0 0.5rem; }
.mon-card {
    background:#fff1f2;border:1px solid #fecdd3;border-radius:var(--rl);
    padding:1.2rem 1.35rem;margin-bottom:0.75rem;
}
.mon-card-title { font-size:0.92rem;font-weight:700;color:#9f1239;margin:0 0 0.5rem; }
.card-row { font-size:0.82rem;color:var(--txt-mid);margin:0.25rem 0;line-height:1.6; }
.card-row strong { color:var(--navy); }
.tag-green { color:var(--green);font-weight:700; }
.tag-red   { color:var(--red);font-weight:700; }

/* ── HOW IT WORKS (instruction page) ── */
.how-step {
    display:flex;gap:1.25rem;align-items:flex-start;
    background:var(--surface);border:1px solid var(--border);
    border-radius:var(--rl);padding:1.4rem 1.5rem;margin-bottom:0.9rem;
}
.step-num {
    min-width:36px;height:36px;border-radius:50%;
    background:var(--navy);color:#fff;font-weight:700;
    font-size:0.88rem;display:flex;align-items:center;justify-content:center;flex-shrink:0;
}
.step-title { font-weight:700;color:var(--navy);font-size:0.95rem;margin:0 0 0.3rem; }
.step-desc  { color:var(--txt-mid);font-size:0.87rem;line-height:1.7;margin:0; }

/* ── FOOTER ── */
.footer {
    border-top:1px solid var(--border);margin-top:4rem;
    padding:2rem 0 2.5rem;
}
.footer-inner {
    display:flex;flex-wrap:wrap;justify-content:space-between;
    align-items:flex-start;gap:1.5rem;
}
.footer-brand { font-weight:700;font-size:0.98rem;color:var(--navy);margin-bottom:4px; }
.footer-sub   { font-size:0.78rem;color:var(--txt-light); }
.footer-right { text-align:right; }
.footer-right a { color:var(--blue);text-decoration:none;font-weight:600;font-size:0.82rem; }
.footer-legal {
    margin-top:1.5rem;padding-top:1.2rem;border-top:1px solid var(--border);
    font-size:0.74rem;color:var(--txt-light);line-height:1.8;
}

/* ── STREAMLIT OVERRIDES ── */
.main .block-container { padding:0 !important;max-width:100% !important; }
.main { background:var(--bg) !important; }
[data-testid="stSidebar"] {
    background:var(--surface) !important;
    border-right:1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color:var(--txt-dark) !important; }

.stTextArea textarea {
    background:var(--surface) !important;color:var(--txt-dark) !important;
    border:1px solid var(--border) !important;border-radius:var(--r) !important;
    font-family:'Noto Sans Sinhala','DM Sans',sans-serif !important;
    font-size:0.92rem !important;line-height:1.7 !important;
    box-shadow:none !important;
}
.stTextArea textarea:focus {
    border-color:var(--blue) !important;
    box-shadow:0 0 0 3px var(--blue-dim) !important;
}

.stButton > button {
    background:var(--navy) !important;color:#fff !important;
    border:none !important;border-radius:var(--r) !important;
    font-weight:600 !important;font-size:0.87rem !important;
    padding:0.65rem 1.5rem !important;transition:all 0.18s !important;
    letter-spacing:0.01em;
}
.stButton > button:hover {
    background:var(--blue) !important;
    box-shadow:0 4px 16px var(--blue-glow) !important;
    transform:translateY(-1px) !important;
}
.stButton[data-testid*="primary"] > button {
    background:var(--blue) !important;
}

.stNumberInput input {
    background:var(--surface) !important;color:var(--txt-dark) !important;
    border:1px solid var(--border) !important;border-radius:8px !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap:3px;background:var(--surface-2);
    padding:4px;border-radius:var(--r);
    border:1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    background:transparent !important;color:var(--txt-mid) !important;
    border-radius:7px !important;padding:0.5rem 1.1rem !important;
    font-weight:500;font-size:0.85rem;
}
.stTabs [aria-selected="true"] {
    background:var(--surface) !important;color:var(--navy) !important;
    font-weight:600 !important;
    box-shadow:0 1px 3px rgba(0,0,0,0.08) !important;
}

.streamlit-expanderHeader {
    background:var(--surface) !important;color:var(--txt-dark) !important;
    border:1px solid var(--border) !important;border-radius:var(--r) !important;
    font-size:0.88rem !important;
}

.dataframe { background:var(--surface) !important;border-radius:var(--r) !important; }
.dataframe th {
    background:var(--surface-2) !important;color:var(--navy) !important;
    font-weight:600 !important;padding:0.6rem 0.8rem !important;
    font-size:0.82rem !important;
}
.dataframe td {
    background:var(--surface) !important;color:var(--txt-mid) !important;
    padding:0.6rem 0.8rem !important;border-bottom:1px solid var(--border) !important;
    font-size:0.83rem !important;
}

/* Mobile */
@media(max-width:640px){
    .hero-wrap{padding:2rem 1.5rem;}
    .hero-title{font-size:1.7rem;}
    .hero-stats{gap:1.2rem;}
    .topnav{padding:0 1rem;}
    .nav-links{display:none;}
    .page-wrap{padding:1.25rem 0.85rem;}
    .metric-grid{grid-template-columns:1fr 1fr;}
    .how-step{flex-direction:column;}
    .footer-inner{flex-direction:column;}
    .footer-right{text-align:left;}
}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA & CONFIG
# ===============================

STOPWORDS_PATH = "./data/stop words.txt"
CONFIDENCE_THRESHOLD = 0.70

@st.cache_resource(show_spinner=False)
def load_stopwords():
    if not os.path.exists(STOPWORDS_PATH):
        return []
    return open(STOPWORDS_PATH, encoding="utf-8").read().splitlines()

stop_words = load_stopwords()

def tokenizer(text):
    tokens = re.findall(r'\b\w+\b', text.lower())
    return [tk for tk in tokens if tk not in stop_words]

companies = [
    "MCPL.N0000","WATA.N0000","AGPL.N0000","HAPU.N0000",
    "KOTA.N0000","BFL.N0000","RWSL.N0000","DIPP.N0000",
    "MGT.N0000","HEXP.N0000"
]

BEST_MODELS = {c: 'XGBoost' for c in companies}

MODEL_METRICS = {
    'MCPL.N0000': {'XGBoost':0.18,'SARIMAX':13.66,'LightGBM':4.91,  'Hybrid':None},
    'WATA.N0000': {'XGBoost':0.56,'SARIMAX':14.43,'LightGBM':None,  'Hybrid':15.91},
    'AGPL.N0000': {'XGBoost':0.30,'SARIMAX':21.80,'LightGBM':10.00, 'Hybrid':None},
    'HAPU.N0000': {'XGBoost':0.25,'SARIMAX':12.43,'LightGBM':1.58,  'Hybrid':None},
    'KOTA.N0000': {'XGBoost':0.22,'SARIMAX':7.08, 'LightGBM':1.17,  'Hybrid':None},
    'BFL.N0000':  {'XGBoost':0.64,'SARIMAX':16.31,'LightGBM':None,  'Hybrid':10.10},
    'RWSL.N0000': {'XGBoost':1.82,'SARIMAX':29.73,'LightGBM':None,  'Hybrid':31.14},
    'DIPP.N0000': {'XGBoost':0.24,'SARIMAX':11.48,'LightGBM':5.52,  'Hybrid':None},
    'MGT.N0000':  {'XGBoost':0.18,'SARIMAX':21.99,'LightGBM':0.64,  'Hybrid':None},
    'HEXP.N0000': {'XGBoost':0.42,'SARIMAX':16.48,'LightGBM':4.85,  'Hybrid':None},
}

SPLIT_COMPANIES = {
    'WATA.N0000': {'date':'2025-03-03','ratio':5,'adjusted':True},
    'BFL.N0000':  {'date':'2023-08-01','ratio':5,'adjusted':True},
}

company_data = {
    'MCPL.N0000': {'name':'Mahaweli Coconut Plantations PLC','symbol':'MCPL','sector':'Plantations',     'default_price':50.50, 'color':'#0ea5e9'},
    'WATA.N0000': {'name':'Watawala Plantations PLC',        'symbol':'WATA','sector':'Plantations',     'default_price':180.00,'color':'#10b981'},
    'AGPL.N0000': {'name':'Agarapatana Plantations PLC',     'symbol':'AGPL','sector':'Plantations',     'default_price':22.00, 'color':'#14b8a6'},
    'HAPU.N0000': {'name':'Hapugastenne Plantations PLC',    'symbol':'HAPU','sector':'Plantations',     'default_price':74.00, 'color':'#06b6d4'},
    'KOTA.N0000': {'name':'Kotagala Plantations PLC',        'symbol':'KOTA','sector':'Plantations',     'default_price':9.80,  'color':'#3b82f6'},
    'BFL.N0000':  {'name':'Bairaha Farms PLC',               'symbol':'BFL', 'sector':'Food & Beverage', 'default_price':300.00,'color':'#6366f1'},
    'RWSL.N0000': {'name':'Raigam Wayamba Salterns PLC',     'symbol':'RWSL','sector':'Manufacturing',   'default_price':27.50, 'color':'#8b5cf6'},
    'DIPP.N0000': {'name':'Dipped Products PLC',             'symbol':'DIPP','sector':'Manufacturing',   'default_price':68.00, 'color':'#a855f7'},
    'MGT.N0000':  {'name':'Hayleys Fabric PLC',              'symbol':'MGT', 'sector':'Plantations',     'default_price':42.50, 'color':'#d946ef'},
    'HEXP.N0000': {'name':'Hayleys Fibre PLC',               'symbol':'HEXP','sector':'Export & Trading','default_price':95.00, 'color':'#ec4899'},
}

# ===============================
# MODEL LOADING
# ===============================

@st.cache_resource(show_spinner=False)
def load_all_models():
    models = {k: {} for k in ['sentiment','xgboost','sarimax','lightgbm','hybrid',
                                'xgboost_scalers','lightgbm_scalers','hybrid_scalers',
                                'xgboost_features','lightgbm_features','hybrid_weights','metadata']}
    status = {k: {} for k in ['sentiment','xgboost','sarimax','lightgbm','hybrid']}

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
        lbl  = f"{bm}" if mape else bm
        return pred,conf,lbl
    pred,conf = predict_xgboost(company,ss,pc,date)
    if pred is not None:
        return pred,conf,"Forecasting Engine"
    return None,0,"Unavailable"

# ===============================
# SENTIMENT
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
# NAVIGATION BAR
# ===============================

sl = sum(1 for s in model_status['sentiment'].values() if s.get('loaded'))
xl = sum(1 for s in model_status['xgboost'].values()   if s.get('loaded'))
all_ok = (sl + xl) > 0

nav_label_home = t("මුල් පිටුව", "Home")
nav_label_how  = t("භාවිතා කරන ආකාරය", "How to Use")
nav_label_about= t("ගැන", "About")

st.markdown(f"""
<div class="topnav">
    <div class="nav-brand">
        <span class="nav-brand-dot"></span>
        SentiTrade
    </div>
    <div class="nav-links" id="navlinks">
        <span class="nav-link {'active' if st.session_state.nav_page=='home'  else ''}"
              onclick="void(0)">{nav_label_home}</span>
        <span class="nav-link {'active' if st.session_state.nav_page=='how'   else ''}"
              onclick="void(0)">{nav_label_how}</span>
        <span class="nav-link {'active' if st.session_state.nav_page=='about' else ''}"
              onclick="void(0)">{nav_label_about}</span>
    </div>
    <div class="nav-right">
        <span class="nav-badge">
            <span class="dot {'dot-on' if all_ok else 'dot-off'}"></span>
            {'Ready' if all_ok else 'Loading'}
        </span>
        <span class="nav-badge">v1.0.0</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Streamlit nav buttons (hidden visually but functional via sidebar)
# Use sidebar for nav

# ===============================
# SIDEBAR
# ===============================

with st.sidebar:
    st.markdown("""
    <div style='padding:1.2rem 0 0.5rem;'>
        <div style='font-weight:700;font-size:1rem;color:#0f172a;'>SentiTrade</div>
        <div style='font-size:0.72rem;color:#94a3b8;margin-top:2px;'>
            Colombo Stock Exchange · v1.0.0
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Language
    st.markdown(f"<div style='font-size:0.7rem;font-weight:700;color:#94a3b8;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;'>{t('භාෂාව','Language')}</div>", unsafe_allow_html=True)
    la, lb = st.columns(2)
    with la:
        if st.button("සිංහල", use_container_width=True,
                     type="primary" if st.session_state.lang=="si" else "secondary"):
            st.session_state.lang = "si"; st.rerun()
    with lb:
        if st.button("English", use_container_width=True,
                     type="primary" if st.session_state.lang=="en" else "secondary"):
            st.session_state.lang = "en"; st.rerun()

    st.markdown("---")

    # Navigation
    st.markdown(f"<div style='font-size:0.7rem;font-weight:700;color:#94a3b8;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;'>{t('සෙවිය','Navigate')}</div>", unsafe_allow_html=True)

    pages = {
        "home":  t("මුල් පිටුව — විශ්ලේෂණය", "Home — Run Analysis"),
        "how":   t("භාවිතා කරන ආකාරය",        "How to Use"),
        "about": t("SentiTrade ගැන",            "About SentiTrade"),
    }
    for pg_key, pg_label in pages.items():
        if st.button(pg_label, use_container_width=True,
                     type="primary" if st.session_state.nav_page==pg_key else "secondary",
                     key=f"nav_{pg_key}"):
            st.session_state.nav_page = pg_key; st.rerun()

    st.markdown("---")

    # System status — plain language
    st.markdown(f"<div style='font-size:0.7rem;font-weight:700;color:#94a3b8;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;'>{t('පද්ධති තත්ත්වය','System Status')}</div>", unsafe_allow_html=True)

    status_items = [
        (t("ප්‍රවෘත්ති විශ්ලේෂණය","News Analysis"),    sl,  10),
        (t("මිල පූර්වාවලෝකනය","Price Forecasting"),   xl,  10),
    ]
    for label, loaded, total in status_items:
        dc = "dot-on" if loaded > 0 else "dot-off"
        status_txt = t("සූදානම්","Ready") if loaded > 0 else t("නොමැත","Unavailable")
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:4px 0;">'
            f'<span><span class="dot {dc}"></span>'
            f'<span style="color:#475569;font-size:0.83rem;">{label}</span></span>'
            f'<span style="color:#94a3b8;font-size:0.76rem;">{status_txt}</span>'
            f'</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Date
    st.markdown(f"<div style='font-size:0.7rem;font-weight:700;color:#94a3b8;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;'>{t('විශ්ලේෂණ දිනය','Analysis Date')}</div>", unsafe_allow_html=True)
    analysis_date = st.date_input("", value=datetime.now(), label_visibility="collapsed")

    st.markdown("---")
    st.markdown("""
    <div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:0.9rem;'>
        <div style='font-weight:600;color:#0f172a;font-size:0.85rem;'>Huzaifa Ameer</div>
        <div style='color:#94a3b8;font-size:0.74rem;margin:2px 0 6px;'>AI/ML Engineer</div>
        <a href='https://www.linkedin.com/in/huzaifaameer/' target='_blank'
           style='color:#1d4ed8;font-size:0.74rem;text-decoration:none;font-weight:600;'>
           LinkedIn Profile
        </a>
    </div>
    """, unsafe_allow_html=True)

# ===============================
# PAGE: HOW TO USE
# ===============================

if st.session_state.nav_page == "how":
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    st.markdown(f"""
    <div style='margin-bottom:2rem;'>
        <div style='font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;
                    color:#94a3b8;margin-bottom:0.6rem;'>
            {t('මාර්ගෝපදේශය','User Guide')}
        </div>
        <h2 style='font-size:2rem;font-weight:700;color:#0f172a;margin:0 0 0.6rem;letter-spacing:-0.5px;'>
            {t('SentiTrade භාවිතා කරන ආකාරය','How to Use SentiTrade')}
        </h2>
        <p style='color:#475569;font-size:0.96rem;max-width:640px;line-height:1.75;margin:0;'>
            {t(
                'ඔබ කොටස් ගැන ස්වාභාවිකව දැනුවත් නොවූ කෙනෙකු වුවත් SentiTrade ඉතා පහසුවෙන් භාවිතා කළ හැකිය.',
                'Even if you have no background in stocks or technology, SentiTrade is designed to be simple and clear.'
            )}
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.lang == "si":
        steps = [
            ("1", "සිංහල ව්‍යාපාරික පුවත් ලිපිය ඇතුළු කරන්න",
             "ඔබ කියවූ ඕනෑම සිංහල ව්‍යාපාරික පුවතක් 'ලිපිය 1' කොටුවට අලවන්න. "
             "ලිපි කිහිපයක් ඇතුළු කිරීමෙන් ප්‍රතිඵල වඩාත් නිවැරදි වේ. "
             "සිංහල භාෂාවෙන් ලිවූ ව්‍යාපාරික ලිපි පමණක් ඇතුළු කරන්න."),
            ("2", "ඊයේ වසා දැමූ කොටස් මිල ඇතුළු කරන්න",
             "සෑම සමාගමකටම ඊයේ දිනයේ කොළඹ කොටස් හුවමාරුවේ (CSE) වසා දැමූ කොටස් මිල රුපියල් ඒකකයෙන් ඇතුළු කරන්න. "
             "ඔබ මෙය නොදනී නම්, CSE.lk වෙබ් අඩවියෙන් හෝ ඔබේ stockbroker ගෙන් ලබා ගත හැකිය."),
            ("3", "දිනය තෝරාගන්න",
             "Sidebar (වම් පැත්ත) හි ඇති 'Analysis Date' (විශ්ලේෂණ දිනය) තේරීම ගෙන් ඔබට අදාළ දිනය තෝරාගන්න. "
             "සාමාන්‍යයෙන් අද දිනය හෝ ඊළඟ ව්‍යාපාරික දිනය භාවිතා කරන්න."),
            ("4", "විශ්ලේෂණය ක්‍රියාත්මක කරන්න",
             "'Run Analysis' බොත්තම ඔබන්න. SentiTrade ඔබ ඇතුළු කළ ලිපිවල ධනාත්මක හෝ ඍණාත්මක ව්‍යාපාරික ස්වභාවය "
             "හඳුනාගෙන, ඉදිරි කොටස් මිල ගණනය කරයි."),
            ("5", "ප්‍රතිඵල කියවන්න",
             "ප්‍රතිඵල පිටුවේ, සෑම සමාගමකටම ඊළඟ ව්‍යාපාරික දිනයේ අපේක්ෂිත මිල, ඊයේ මිලට සාපේක්ෂව වෙනස (+ හෝ −), "
             "සහ ප්‍රවෘත්තිවලින් ගත් ව්‍යාපාරික ස්වභාවය (ධනාත්මක/ඍණාත්මක/මධ්‍යස්ථ) දැකිය හැකිය."),
            ("6", "ප්‍රතිඵල බාගත කරන්න",
             "ඔබට අවශ්‍ය නම් 'Export' කොටසෙන් ප්‍රතිඵල CSV ගොනුවක් ලෙස සුරකිය හැකිය. "
             "ඔබේ broker සහ reference සඳහා ඉතා ප්‍රයෝජනවත් වේ."),
        ]
    else:
        steps = [
            ("1", "Paste your Sinhala business news article",
             "Copy and paste any Sinhala-language business news article into the 'Article 1' box. "
             "Adding more articles improves the accuracy of the forecast. "
             "Make sure the text is written in Sinhala — English articles won't be analysed correctly."),
            ("2", "Enter yesterday's closing stock price",
             "For each company, enter the price at which its shares closed on the Colombo Stock Exchange (CSE) yesterday. "
             "You can find these prices on CSE.lk, your stockbroker's app, or a financial news site."),
            ("3", "Select the analysis date",
             "Use the 'Analysis Date' picker in the left sidebar to choose the date you want to forecast for. "
             "Typically this is today or the next trading day."),
            ("4", "Run the analysis",
             "Click 'Run Analysis'. SentiTrade will read your news articles, determine whether the business sentiment is "
             "positive, negative, or neutral, and calculate an expected price for each company."),
            ("5", "Read your results",
             "In the results section, you'll see each company's expected price for the next trading day, "
             "the change compared to yesterday (+ or −), and the news sentiment (Positive / Negative / Neutral) "
             "that influenced the forecast."),
            ("6", "Download your report",
             "Use the Export section at the bottom of the results to download a CSV file of all predictions "
             "and sentiment scores — useful for sharing with your stockbroker or keeping records."),
        ]

    for num, title, desc in steps:
        st.markdown(f"""
        <div class="how-step">
            <div class="step-num">{num}</div>
            <div>
                <div class="step-title">{title}</div>
                <p class="step-desc">{desc}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="warn-box" style='margin-top:2rem;'>
        <strong>{t('වැදගත් සටහන','Important Note')} —</strong>
        {t(
            'SentiTrade ප්‍රවෘත්ති-ආශ්‍රිත සිදුවිය හැකි දිශාවක් (direction) සලකා බැලේ. '
            'මෙය ආයෝජන උපදෙසක් නොවේ. ඕනෑම ආයෝජන තීරණයක් ගැනීමට පෙර ලිදෙනු ලබා ශ්‍රේණිගත broker හෝ '
            'මූල්‍ය උපදේශකයකු හමුවන්න.',
            'SentiTrade estimates a likely direction based on news sentiment — it is not a guarantee of future prices. '
            'Always consult a licensed stockbroker or financial adviser before making investment decisions.'
        )}
    </div>
    """, unsafe_allow_html=True)

    # FAQ
    st.markdown(f"""
    <div style='margin-top:2.5rem;'>
        <div style='font-weight:700;font-size:1rem;color:#0f172a;margin-bottom:1rem;'>
            {t('නිතර අසන ප්‍රශ්න','Frequently Asked Questions')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.lang == "si":
        faqs = [
            ("සිංහල ලිපි ඇතුළු නොකළොත් කුමක් සිදු වේද?",
             "ඇල්ගොරිතමය ලිපිවල ස්වභාවය හඳුනාගත නොහැකි බැවින් ප්‍රතිඵල නිවැරදි නොවිය හැකිය. "
             "හැකිතාක් සිංහල ව්‍යාපාරික ලිපිම ඇතුළු කරන්න."),
            ("WATA සහ BFL කොටස් 'split adjusted' ලෙස සලකනු ලබන්නේ ඇයි?",
             "WATA 2025 සහ BFL 2023 දී 1:5 කොටස් බෙදීම (stock split) සිදු කළේය. "
             "ඒ නිසා, ඔබ ඇතුළු කරන මිල split-adjusted (බෙදීමෙන් පසු) මිල විය යුතුය. "
             "ගණනය කරන ලද අනාවැකි ද split-adjusted මිල ලෙස ප්‍රදර්ශනය වේ."),
            ("ලිපි කීයක් ඇතුළු කළ හොත් හොඳ ද?",
             "ලිපි 3-5 ක් ඇතුළු කිරීමෙන් ප්‍රතිඵල ස්ථාවර සහ නිවැරදි ලෙස ලැබේ."),
        ]
    else:
        faqs = [
            ("What happens if I enter English news instead of Sinhala?",
             "The sentiment engine was trained on Sinhala business language, so English text will not be analysed correctly. "
             "For best results, always use Sinhala-language articles."),
            ("Why are WATA and BFL marked 'split-adjusted'?",
             "Watawala Plantations (WATA) underwent a 1-for-5 stock split in March 2025, and Bairaha Farms (BFL) in August 2023. "
             "The prices you enter and the predictions shown are already adjusted for these splits, so they reflect the current share price level."),
            ("How many articles should I add for best results?",
             "Three to five articles from recent Sinhala business news gives a well-rounded sentiment signal and more stable forecasts."),
        ]

    for q, a in faqs:
        with st.expander(q):
            st.markdown(f"<p style='color:#475569;font-size:0.88rem;line-height:1.75;margin:0;'>{a}</p>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# PAGE: ABOUT
# ===============================

elif st.session_state.nav_page == "about":
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    st.markdown(f"""
    <div style='margin-bottom:2rem;'>
        <div style='font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;
                    color:#94a3b8;margin-bottom:0.6rem;'>About</div>
        <h2 style='font-size:2rem;font-weight:700;color:#0f172a;margin:0 0 0.6rem;letter-spacing:-0.5px;'>
            {t('SentiTrade ගැන','About SentiTrade')}
        </h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='card card-accent' style='margin-bottom:1.25rem;'>
        <div style='font-weight:700;color:#0f172a;font-size:0.97rem;margin-bottom:0.6rem;'>
            {t('SentiTrade යනු කුමක් ද?','What is SentiTrade?')}
        </div>
        <p style='color:#475569;font-size:0.9rem;line-height:1.8;margin:0;'>
            {t(
                'SentiTrade යනු සිංහල ව්‍යාපාරික ප්‍රවෘත්ති කියවා, ඒවා ධනාත්මක ද ඍණාත්මක ද යන්න '
                'තේරුම් ගෙන, ඒ අනුව කොළඹ කොටස් හුවමාරුවේ ලැයිස්තුගත සමාගම් 10ක ඊළඟ ව්‍යාපාරික දිනයේ '
                'කොටස් මිල ගණනය කරන AI-ශක්තිමත් යෙදවුමකි. සරලව කිවහොත්, ව්‍යාපාරික ප්‍රවෘත්ති '
                'සහ ඊයේ කොටස් මිල ඇතුළු කළ විට, SentiTrade හෙට කොටස් මිල කොතැනට යයිද යන්න '
                'ඇස්තමේන්තු කරයි.',
                'SentiTrade is an AI-powered application that reads Sinhala business news, '
                'determines whether the tone is positive or negative, and uses that information '
                'alongside yesterday\'s prices to estimate where stock prices for 10 CSE-listed '
                'companies may move on the next trading day. In plain terms: give it news and '
                'a price, and it gives you a direction.'
            )}
        </p>
    </div>

    <div class='card' style='margin-bottom:1.25rem;'>
        <div style='font-weight:700;color:#0f172a;font-size:0.97rem;margin-bottom:0.6rem;'>
            {t('ආවරණය කරන සමාගම්','Companies Covered')}
        </div>
        <p style='color:#475569;font-size:0.88rem;line-height:1.8;margin:0 0 0.8rem;'>
            {t(
                'SentiTrade කොළඹ කොටස් හුවමාරුවේ ලැයිස්තුගත සමාගම් 10ක් ආවරණය කරයි:',
                'SentiTrade covers the following 10 CSE-listed companies:'
            )}
        </p>
    </div>
    """, unsafe_allow_html=True)

    rows = []
    for c in companies:
        sp = SPLIT_COMPANIES.get(c)
        rows.append({
            t("සිරස","Symbol"): company_data[c]['symbol'],
            t("සමාගම","Company"): company_data[c]['name'],
            t("අංශය","Sector"): company_data[c]['sector'],
            t("කොටස් බෙදීම","Split"): f"1:5 ({sp['date']})" if sp else "—",
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    st.markdown(f"""
    <div class='info-box' style='margin-top:1.5rem;'>
        <strong>{t('නිෂ්පාදකයා','Developer')} —</strong>
        {t(
            'SentiTrade නිෂ්පාදනය කළේ AI/ML ඉංජිනේරු Huzaifa Ameer විසිනි. '
            'LinkedIn: linkedin.com/in/huzaifaameer',
            'SentiTrade was developed by Huzaifa Ameer, AI/ML Engineer. '
            'LinkedIn: linkedin.com/in/huzaifaameer'
        )}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# PAGE: HOME (MAIN ANALYSIS)
# ===============================

else:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    # ── HERO ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero-wrap">
        <div class="hero-label">
            <span></span>
            CSE · Colombo Stock Exchange · Sinhala News Intelligence
        </div>
        <h1 class="hero-title">
            {t('<em>සිංහල</em> ප්‍රවෘත්තිවලින්<br>කොටස් මිල ගණනය කරන්න',
               'Forecast CSE stock prices<br>from <em>Sinhala</em> news')}
        </h1>
        <p class="hero-desc">
            {t(
                'ඔබ කියවූ සිංහල ව්‍යාපාරික ප්‍රවෘත්ති ලිපිය ඇතුළු කර, ඊයේ කොටස් මිල '
                'ඇතුළු කරන්න. SentiTrade ඔබට ඊළඟ ව්‍යාපාරික දිනය සඳහා '
                'කොළඹ කොටස් හුවමාරුවේ සමාගම් 10ක ඇස්තමේන්තු ලබා දේ.',
                'Enter a Sinhala business news article and yesterday\'s closing prices. '
                'SentiTrade will estimate the next trading day\'s prices for '
                '10 Colombo Stock Exchange companies.'
            )}
        </p>
        <div class="hero-stats">
            <div>
                <div class="hero-stat-val">10</div>
                <div class="hero-stat-lbl">{t('සමාගම්','Companies')}</div>
            </div>
            <div>
                <div class="hero-stat-val">CSE</div>
                <div class="hero-stat-lbl">{t('කොළඹ කොටස් හුවමාරුව','Colombo Stock Exchange')}</div>
            </div>
            <div>
                <div class="hero-stat-val">{t('සිංහල','Sinhala')}</div>
                <div class="hero-stat-lbl">{t('ප්‍රවෘත්ති ආශ්‍රිත','News-Driven')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── INPUT ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class='sec-hdr'>
        <span class='sec-hdr-title'>{t('දත්ත ඇතුළත් කිරීම','Data Input')}</span>
        <span class='sec-hdr-line'></span>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs([
        t("ප්‍රවෘත්ති ලිපි", "News Articles"),
        t("කොටස් මිල", "Stock Prices"),
    ])

    with tab1:
        st.markdown(f"""
        <div class='info-box'>
            {t(
                '<strong>සිංහල ව්‍යාපාරික ලිපි පමණක් ඇතුළු කරන්න.</strong> '
                'ලිපි 3-5 ක් ඇතුළු කිරීමෙන් ප්‍රතිඵල වඩාත් නිවැරදි ලෙස ලැබේ.',
                '<strong>Sinhala business news articles only.</strong> '
                'Adding 3–5 articles improves forecast accuracy.'
            )}
        </div>
        """, unsafe_allow_html=True)

        if "news_inputs" not in st.session_state:
            st.session_state.news_inputs = [""]

        ca, cb, cc = st.columns([3,1,1])
        with cb:
            if st.button(t("ලිපිය එකතු කරන්න", "Add Article"), use_container_width=True):
                st.session_state.news_inputs.append(""); st.rerun()
        with cc:
            if st.button(t("සියල්ල මකන්න", "Clear All"), use_container_width=True):
                st.session_state.news_inputs = [""]; st.rerun()

        news_texts = []
        for i in range(len(st.session_state.news_inputs)):
            news = st.text_area(
                f"{t('ලිපිය','Article')} {i+1}",
                height=130,
                value=st.session_state.news_inputs[i],
                key=f"news_{i}",
                placeholder=t(
                    "සිංහල ව්‍යාපාරික ප්‍රවෘත්ති ලිපිය මෙහි ඇලවන්න… "
                    "(උදා: 'ලංකා IOC හි ලාභය රු. මිලියන 450 ඉක්මවා ඇත.')",
                    "Paste a Sinhala business news article here… "
                    "(e.g., 'Lanka IOC profits cross Rs. 450 million.')"
                )
            )
            news_texts.append(news)
            st.session_state.news_inputs[i] = news

    with tab2:
        st.markdown(f"""
        <div class='info-box'>
            {t(
                '<strong>ඊයේ (previous day) CSE හි වසා දැමූ කොටස් මිල</strong> '
                'රුපියල් (Rs.) ඒකකයෙන් ඇතුළු කරන්න.',
                'Enter each company\'s <strong>previous day closing price</strong> '
                'from the CSE, in Sri Lankan Rupees (Rs.).'
            )}
        </div>
        """, unsafe_allow_html=True)

        # Show split note once
        if any(c in SPLIT_COMPANIES for c in companies):
            st.markdown(f"""
            <div class='warn-box'>
                {t(
                    '<strong>WATA සහ BFL:</strong> මෙම සමාගම් දෙකේ කොටස් සිතා බෙදීමෙන් (stock split) '
                    'ලැබෙන මිල ඇතුළු කරන්න. WATA — 2025 මාර්තු (1:5), BFL — 2023 අගෝස්තු (1:5).',
                    '<strong>WATA and BFL:</strong> Enter the current post-split price for these companies. '
                    'WATA split 1-for-5 in March 2025; BFL split 1-for-5 in August 2023.'
                )}
            </div>
            """, unsafe_allow_html=True)

        prev_close_prices = {}
        sectors = {}
        for c in companies:
            sectors.setdefault(company_data[c]['sector'], []).append(c)

        for sector, sector_cos in sectors.items():
            with st.expander(f"{sector}", expanded=True):
                cols = st.columns(min(3, len(sector_cos)))
                for idx, c in enumerate(sector_cos):
                    with cols[idx % 3]:
                        info = company_data[c]
                        split_tag = ""
                        if c in SPLIT_COMPANIES:
                            split_tag = f" <span style='font-size:0.65rem;color:#d97706;background:#fffbeb;border:1px solid #fde68a;border-radius:4px;padding:1px 5px;'>split-adj</span>"
                        st.markdown(f"<div style='font-weight:600;font-size:0.88rem;color:#0f172a;margin-bottom:2px;'>{info['symbol']}{split_tag}</div>", unsafe_allow_html=True)
                        st.caption(info['name'][:28] + "…")
                        prev_close_prices[c] = st.number_input(
                            t("Rs.", "Rs."),
                            min_value=0.0,
                            value=info['default_price'],
                            step=0.1,
                            format="%.2f",
                            key=f"price_{c}",
                            label_visibility="visible"
                        )

    # ── ANALYSE BUTTON ────────────────────────────────────────────────────────
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([1.5, 2, 1.5])
    with btn_col:
        analyze_button = st.button(
            t("විශ්ලේෂණය ක්‍රියාත්මක කරන්න", "Run Analysis"),
            type="primary", use_container_width=True
        )

    # ===============================
    # ANALYSIS EXECUTION
    # ===============================

    if analyze_button:
        if all(tx.strip() == "" for tx in news_texts):
            st.warning(t(
                "අවම වශයෙන් එක් සිංහල ලිපියක් ඇතුළු කරන්න.",
                "Please enter at least one Sinhala news article."
            ))
            st.stop()

        pb = st.progress(0)
        st_txt = st.empty()

        # Sentiment
        st_txt.markdown(f"<div style='color:#475569;font-size:0.87rem;padding:0.4rem 0;'>{t('ලිපිවල ව්‍යාපාරික ස්වභාවය විශ්ලේෂණය කරමින්…','Reading news sentiment…')}</div>", unsafe_allow_html=True)
        sent_res = []
        for idx, text in enumerate(news_texts, 1):
            if text.strip() == "": continue
            row = {
                t("ලිපිය","Article"): f"{t('ලිපිය','Article')} {idx}",
                t("පෙරදසුන","Preview"): text[:100] + "…"
            }
            for c in companies:
                row[c] = analyze_sentiment(text, c)
            sent_res.append(row)
            pb.progress(int((idx / len(news_texts)) * 40))

        sentiment_df = pd.DataFrame(sent_res)
        smap = {"Positive": 1, "Neutral": 0, "Negative": -1}
        score_mx = sentiment_df[[c for c in companies if c in sentiment_df.columns]].copy()
        for c in companies:
            if c in score_mx.columns:
                score_mx[c] = score_mx[c].map(smap)
        daily_scores = score_mx.mean().reset_index()
        daily_scores.columns = ["Company", "Average_Sentiment_Score"]

        # Predictions
        st_txt.markdown(f"<div style='color:#475569;font-size:0.87rem;padding:0.4rem 0;'>{t('ඊළඟ ව්‍යාපාරික දිනය සඳහා මිල ගණනය කරමින්…','Calculating price estimates…')}</div>", unsafe_allow_html=True)
        preds_list, failed = [], []

        for idx, (_, row_d) in enumerate(daily_scores.iterrows()):
            company = row_d["Company"]
            ss = row_d["Average_Sentiment_Score"]
            pc = prev_close_prices.get(company, company_data[company]['default_price'])
            pred_price, conf, model_used = predict_best(company, ss, pc, analysis_date)

            if pred_price is None:
                failed.append(company_data[company]['symbol'])
                continue

            chg_amt = pred_price - pc
            chg_pct = (chg_amt / pc) * 100 if pc > 0 else 0

            # Display prices for split-adjusted companies (show as-is; they are already split-adjusted)
            display_prev  = pc
            display_pred  = pred_price
            split_note    = ""
            if company in SPLIT_COMPANIES:
                split_note = t(
                    f"(split-adj · 1:5 · {SPLIT_COMPANIES[company]['date']})",
                    f"(split-adj · 1:5 · {SPLIT_COMPANIES[company]['date']})"
                )

            preds_list.append({
                "Company":               company_data[company]['name'],
                "Symbol":                company_data[company]['symbol'],
                "Sector":                company_data[company]['sector'],
                "Previous_Close":        display_prev,
                "Predicted_Price":       display_pred,
                "Price_Change":          chg_amt,
                "Price_Change_Percent":  chg_pct,
                "Sentiment_Score":       ss,
                "Sentiment_Category":    "Positive" if ss > 0.1 else "Negative" if ss < -0.1 else "Neutral",
                "Model_Used":            model_used,
                "Confidence":            conf,
                "Split_Adjusted":        company in SPLIT_COMPANIES,
                "Split_Note":            split_note,
                "Color":                 company_data[company]['color'],
            })
            pb.progress(40 + int(((idx + 1) / len(companies)) * 60))

        pb.empty()
        st_txt.empty()

        if failed:
            st.warning(f"{t('ගණනය නොකළ හැකි','Could not forecast')}: {', '.join(failed)}")
        if not preds_list:
            st.error(t("ගණනය කිරීම අසාර්ථකයි.", "No predictions could be generated."))
            st.stop()

        predictions_df = pd.DataFrame(preds_list)

        # ── RESULTS ────────────────────────────────────────────────────────
        st.markdown(f"""
        <div class='sec-hdr'>
            <span class='sec-hdr-title'>{t('ප්‍රතිඵල','Results')}</span>
            <span class='sec-hdr-line'></span>
        </div>
        """, unsafe_allow_html=True)

        # Summary metrics
        avg_ret = predictions_df['Price_Change_Percent'].mean()
        pos_n   = len(predictions_df[predictions_df['Price_Change_Percent'] > 0])
        neg_n   = len(predictions_df[predictions_df['Price_Change_Percent'] < 0])
        bstp    = predictions_df.loc[predictions_df['Price_Change_Percent'].idxmax()]
        avg_snt_raw = predictions_df['Sentiment_Score'].mean()
        snt_label   = t("ධනාත්මක","Positive") if avg_snt_raw > 0.1 else t("ඍණාත්මක","Negative") if avg_snt_raw < -0.1 else t("මධ්‍යස්ථ","Neutral")

        st.markdown(f"""
        <div class='metric-grid'>
            <div class='metric-card'>
                <div class='metric-val'>{avg_ret:+.1f}%</div>
                <div class='metric-lbl'>{t('සාමාන්‍ය ඇස්තමේන්තු වෙනස','Avg Estimated Change')}</div>
            </div>
            <div class='metric-card'>
                <div class='metric-val'>{pos_n}</div>
                <div class='metric-lbl'>{t('ලාභ ඇස්තමේන්තු','Estimated Gainers')}</div>
                <div class='metric-delta-dn'>{neg_n} {t('පහත','downward')}</div>
            </div>
            <div class='metric-card'>
                <div class='metric-val'>{snt_label}</div>
                <div class='metric-lbl'>{t('ප්‍රවෘත්ති ස්වභාවය','Overall News Tone')}</div>
            </div>
            <div class='metric-card'>
                <div class='metric-val'>{bstp['Symbol']}</div>
                <div class='metric-lbl'>{t('ඉහළම ඇස්තමේන්තු','Highest Estimate')}</div>
                <div class='metric-delta-up'>{bstp['Price_Change_Percent']:+.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Sentiment table
        st.markdown(f"""
        <div class='sec-hdr'>
            <span class='sec-hdr-title'>{t('ප්‍රවෘත්ති ස්වභාවය · ලිපි අනුව','News Tone per Article')}</span>
            <span class='sec-hdr-line'></span>
        </div>
        """, unsafe_allow_html=True)

        ad = sentiment_df.copy()
        rd = {}
        for c in companies:
            if c in ad.columns:
                rd[c] = company_data[c]['symbol']
        ad = ad.rename(columns=rd)

        def _sty(val):
            if val == "Positive": return 'background-color:#f0fdf4;color:#065f46;font-weight:600;'
            if val == "Negative": return 'background-color:#fff1f2;color:#9f1239;font-weight:600;'
            if val == "Neutral":  return 'background-color:#f8fafc;color:#475569;'
            return ''

        sym_cols = [company_data[c]['symbol'] for c in companies if company_data[c]['symbol'] in ad.columns]
        st.dataframe(ad.style.map(_sty, subset=sym_cols), use_container_width=True, height=320)

        # Price predictions table
        st.markdown(f"""
        <div class='sec-hdr'>
            <span class='sec-hdr-title'>{t('ඇස්තමේන්තු කොටස් මිල','Estimated Stock Prices')}</span>
            <span class='sec-hdr-line'></span>
        </div>
        """, unsafe_allow_html=True)

        disp = predictions_df.copy()
        disp['Prev_Close_Display']    = disp.apply(
            lambda r: f"Rs. {r['Previous_Close']:,.2f}" + (" *" if r['Split_Adjusted'] else ""), axis=1)
        disp['Predicted_Display']     = disp.apply(
            lambda r: f"Rs. {r['Predicted_Price']:,.2f}" + (" *" if r['Split_Adjusted'] else ""), axis=1)
        disp['Change_Display']        = disp['Price_Change_Percent'].map(lambda x: f"{x:+.2f}%")
        disp['Sentiment_Display']     = disp['Sentiment_Category'].map(
            lambda x: t("ධනාත්මක","Positive") if x=="Positive"
                      else t("ඍණාත්මක","Negative") if x=="Negative"
                      else t("මධ්‍යස්ථ","Neutral"))

        col_map = {
            'Symbol':            t('සිරස','Symbol'),
            'Sector':            t('අංශය','Sector'),
            'Prev_Close_Display':t('ඊයේ මිල','Yesterday'),
            'Predicted_Display': t('ඇස්තමේන්තු','Estimated'),
            'Change_Display':    t('වෙනස','Change'),
            'Sentiment_Display': t('ප්‍රවෘත්ති ස්වභාවය','News Tone'),
        }

        def _row_sty(row):
            pct = row['Price_Change_Percent']
            color = '#f0fdf4' if pct > 0 else '#fff1f2' if pct < 0 else ''
            return [f'background:{color}'] * len(row)

        st.dataframe(
            disp[list(col_map.keys())].rename(columns=col_map),
            use_container_width=True, height=380
        )
        st.markdown(f"<p style='font-size:0.74rem;color:#94a3b8;margin-top:4px;'>* {t('split-adjusted මිල','Split-adjusted price (WATA 1:5 Mar 2025 · BFL 1:5 Aug 2023)')}</p>", unsafe_allow_html=True)

        # Charts
        st.markdown(f"""
        <div class='sec-hdr'>
            <span class='sec-hdr-title'>{t('ප්‍රස්ථාර','Charts')}</span>
            <span class='sec-hdr-line'></span>
        </div>
        """, unsafe_allow_html=True)

        _bg = dict(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#475569', family='DM Sans, sans-serif'),
            margin=dict(l=10, r=10, t=44, b=10)
        )

        vt1, vt2 = st.tabs([
            t("ඇස්තමේන්තු මිල වෙනස", "Estimated Price Changes"),
            t("ප්‍රවෘත්ති ස්වභාවය", "News Tone"),
        ])

        with vt1:
            v1, v2 = st.columns(2)
            with v1:
                sdf = predictions_df.sort_values('Price_Change_Percent', ascending=True)
                fig = go.Figure(go.Bar(
                    x=sdf['Price_Change_Percent'], y=sdf['Symbol'], orientation='h',
                    marker_color=['#ef4444' if x < 0 else '#10b981' for x in sdf['Price_Change_Percent']],
                    text=sdf['Price_Change_Percent'].map(lambda x: f"{x:+.1f}%"),
                    textposition='outside'
                ))
                fig.update_layout(
                    title=t("ඇස්තමේන්තු වෙනස (%)","Estimated Change (%)"),
                    xaxis_title=t("වෙනස (%)","Change (%)"),
                    height=420, **_bg
                )
                fig.update_xaxes(gridcolor='#f1f5f9', zerolinecolor='#e2e8f0')
                st.plotly_chart(fig, use_container_width=True)
            with v2:
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=predictions_df['Symbol'], y=predictions_df['Previous_Close'],
                    mode='markers+lines', name=t('ඊයේ','Yesterday'),
                    marker=dict(size=8, color='#94a3b8'),
                    line=dict(color='#cbd5e1', dash='dot')
                ))
                fig2.add_trace(go.Scatter(
                    x=predictions_df['Symbol'], y=predictions_df['Predicted_Price'],
                    mode='markers+lines', name=t('ඇස්තමේන්තු','Estimated'),
                    marker=dict(size=11, color='#1d4ed8'),
                    line=dict(color='#1d4ed8', width=2.5)
                ))
                fig2.update_layout(
                    title=t("ඊයේ vs ඇස්තමේන්තු","Yesterday vs Estimated"),
                    yaxis_title=t("මිල (රු.)","Price (Rs.)"),
                    height=420, **_bg
                )
                fig2.update_yaxes(gridcolor='#f1f5f9')
                st.plotly_chart(fig2, use_container_width=True)

        with vt2:
            v1, v2 = st.columns(2)
            with v1:
                sc = predictions_df['Sentiment_Category'].value_counts()
                color_map = {'Positive':'#10b981','Neutral':'#94a3b8','Negative':'#ef4444'}
                colors = [color_map.get(c, '#94a3b8') for c in sc.index]
                fig3 = go.Figure(go.Pie(
                    labels=[t("ධනාත්මක","Positive") if l=="Positive"
                            else t("ඍණාත්මක","Negative") if l=="Negative"
                            else t("මධ්‍යස්ථ","Neutral") for l in sc.index],
                    values=sc.values, hole=0.46,
                    marker=dict(colors=colors)
                ))
                fig3.update_layout(title=t("ප්‍රවෘත්ති ස්වභාව බෙදාහැරීම","News Tone Distribution"), height=380, **_bg)
                st.plotly_chart(fig3, use_container_width=True)
            with v2:
                sp = predictions_df.groupby('Sector')['Price_Change_Percent'].mean().reset_index()
                fig4 = go.Figure(go.Bar(
                    x=sp['Sector'], y=sp['Price_Change_Percent'],
                    text=sp['Price_Change_Percent'].map(lambda x: f"{x:+.1f}%"),
                    textposition='outside',
                    marker_color=['#10b981' if x > 0 else '#ef4444' for x in sp['Price_Change_Percent']]
                ))
                fig4.update_layout(title=t("අංශය අනුව ඇස්තමේන්තු","By Sector"), height=380, **_bg)
                fig4.update_yaxes(gridcolor='#f1f5f9')
                st.plotly_chart(fig4, use_container_width=True)

        # Recommendations
        st.markdown(f"""
        <div class='sec-hdr'>
            <span class='sec-hdr-title'>{t('සාරාංශය','Summary')}</span>
            <span class='sec-hdr-line'></span>
        </div>
        """, unsafe_allow_html=True)

        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown(f"<div style='font-weight:700;color:#065f46;font-size:0.9rem;margin-bottom:0.75rem;'>{t('ඉහළ ඇස්තමේන්තු','Highest Estimates')}</div>", unsafe_allow_html=True)
            hc = predictions_df[predictions_df['Confidence'] >= CONFIDENCE_THRESHOLD]
            if len(hc) == 0:
                hc = predictions_df
            top3 = hc.nlargest(3, 'Price_Change_Percent')
            for _, row in top3.iterrows():
                sn = f" <span style='font-size:0.7rem;color:#d97706;'>(split-adj)</span>" if row['Split_Adjusted'] else ""
                st.markdown(f"""
                <div class='opp-card'>
                    <div class='opp-card-title'>{row['Symbol']} — {row['Company']}</div>
                    <div class='card-row'>
                        <strong>{t('ඊළඟ ඇස්තමේන්තු','Est. Price')}:</strong>
                        Rs.&nbsp;{row['Predicted_Price']:.2f}{sn}
                        &nbsp;&nbsp;<strong>{t('වෙනස','Change')}:</strong>
                        <span class='tag-green'>{row['Price_Change_Percent']:+.2f}%</span>
                    </div>
                    <div class='card-row'>
                        <strong>{t('ප්‍රවෘත්ති ස්වභාවය','News Tone')}:</strong>
                        {t("ධනාත්මක","Positive") if row['Sentiment_Category']=="Positive"
                          else t("ඍණාත්මක","Negative") if row['Sentiment_Category']=="Negative"
                          else t("මධ්‍යස්ථ","Neutral")}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with rc2:
            st.markdown(f"<div style='font-weight:700;color:#9f1239;font-size:0.9rem;margin-bottom:0.75rem;'>{t('අඩු ඇස්තමේන්තු','Lowest Estimates')}</div>", unsafe_allow_html=True)
            bot3 = predictions_df.nsmallest(3, 'Price_Change_Percent')
            for _, row in bot3.iterrows():
                sn = f" <span style='font-size:0.7rem;color:#d97706;'>(split-adj)</span>" if row['Split_Adjusted'] else ""
                st.markdown(f"""
                <div class='mon-card'>
                    <div class='mon-card-title'>{row['Symbol']} — {row['Company']}</div>
                    <div class='card-row'>
                        <strong>{t('ඊළඟ ඇස්තමේන්තු','Est. Price')}:</strong>
                        Rs.&nbsp;{row['Predicted_Price']:.2f}{sn}
                        &nbsp;&nbsp;<strong>{t('වෙනස','Change')}:</strong>
                        <span class='tag-red'>{row['Price_Change_Percent']:+.2f}%</span>
                    </div>
                    <div class='card-row'>
                        <strong>{t('ප්‍රවෘත්ති ස්වභාවය','News Tone')}:</strong>
                        {t("ධනාත්මක","Positive") if row['Sentiment_Category']=="Positive"
                          else t("ඍණාත්මක","Negative") if row['Sentiment_Category']=="Negative"
                          else t("මධ්‍යස්ථ","Neutral")}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Export
        st.markdown(f"""
        <div class='sec-hdr'>
            <span class='sec-hdr-title'>{t('ගොනු බාගත කිරීම','Export')}</span>
            <span class='sec-hdr-line'></span>
        </div>
        """, unsafe_allow_html=True)

        e1, e2, e3 = st.columns(3)
        with e1:
            st.download_button(
                t("ඇස්තමේන්තු (.csv)", "Predictions (.csv)"),
                predictions_df.to_csv(index=False),
                f"predictions_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv", use_container_width=True
            )
        with e2:
            st.download_button(
                t("ප්‍රවෘත්ති ස්වභාවය (.csv)", "Sentiment (.csv)"),
                sentiment_df.to_csv(index=False),
                f"sentiment_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv", use_container_width=True
            )
        with e3:
            full = predictions_df.copy()
            full['Analysis_Date']     = analysis_date
            full['Articles_Analysed'] = len([tx for tx in news_texts if tx.strip()])
            st.download_button(
                t("සම්පූර්ණ වාර්තාව (.csv)", "Full Report (.csv)"),
                full.to_csv(index=False),
                f"full_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv", use_container_width=True
            )

        # Disclaimer
        st.markdown(f"""
        <div class='warn-box' style='margin-top:1.5rem;'>
            <strong>{t('නිෂ්ක්‍රීය ප්‍රකාශය','Disclaimer')} —</strong>
            {t(
                'SentiTrade ලබා දෙන ඇස්තමේන්තු ප්‍රවෘත්ති-ආශ්‍රිත දිශාවකි — '
                'ගැරන්ටියක් නොවේ. අතීත ප්‍රතිඵල අනාගතය සහතික නොකරයි. '
                'ආයෝජන තීරණ ගැනීමේදී ශ්‍රේණිගත stockbroker හෝ මූල්‍ය උපදේශකයකු '
                'හමුවන්න. <strong>මෙය මූල්‍ය උපදෙසක් නොවේ.</strong>',
                'SentiTrade estimates are indicative only and based on news sentiment — '
                'they are not a guarantee of future prices. Past performance does not '
                'predict future results. Consult a licensed stockbroker or financial '
                'adviser before making investment decisions. '
                '<strong>This is not financial advice.</strong>'
            )}
        </div>
        """, unsafe_allow_html=True)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class='footer'>
        <div class='footer-inner'>
            <div>
                <div class='footer-brand'>SentiTrade</div>
                <div class='footer-sub'>
                    Colombo Stock Exchange · Sinhala News Intelligence<br>
                    Version 1.0.0 · 10 Companies · CSE Listed
                </div>
            </div>
            <div class='footer-right'>
                <div style='font-weight:600;font-size:0.85rem;color:#0f172a;margin-bottom:3px;'>Huzaifa Ameer</div>
                <div style='font-size:0.78rem;color:#94a3b8;margin-bottom:5px;'>AI/ML Engineer</div>
                <a href='https://www.linkedin.com/in/huzaifaameer/' target='_blank'>LinkedIn</a>
            </div>
        </div>
        <div class='footer-legal'>
            &copy; 2026 Huzaifa Ameer. All rights reserved.
            SentiTrade is provided for informational purposes only and does not constitute financial advice.
            Forecasts are based on Sinhala news sentiment and historical price data.
            Past results are not indicative of future performance.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)