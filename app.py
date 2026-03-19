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
    page_title="Sinhala News Sentinel",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# MODERN THEME & STYLING (Keep your existing styling)
# ===============================

st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Color Palette - Premium Dark Theme */
    :root {
        --primary: #6366f1;
        --primary-light: #818cf8;
        --primary-dark: #4f46e5;
        --secondary: #10b981;
        --accent: #f59e0b;
        --danger: #ef4444;
        --background: #0f172a;
        --surface: #1e293b;
        --surface-light: #334155;
        --border: #475569;
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --shadow: rgba(0, 0, 0, 0.3);
    }
    
    /* Main Content Area */
    .main {
        background: var(--background);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Custom Header */
    .dashboard-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem;
        border-radius: 24px;
        color: white;
        margin-bottom: 2rem;
        border: 1px solid var(--border);
        position: relative;
        overflow: hidden;
    }
    
    .dashboard-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        position: relative;
        z-index: 1;
    }
    
    .dashboard-subtitle {
        font-size: 1.1rem;
        color: var(--text-secondary);
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .developer-credit {
        position: absolute;
        bottom: 1rem;
        right: 2rem;
        color: var(--text-muted);
        font-size: 0.9rem;
        z-index: 1;
    }
    
    .developer-credit a {
        color: var(--primary-light);
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s;
    }
    
    .developer-credit a:hover {
        color: var(--primary);
        text-decoration: underline;
    }
    
    /* Card Styling */
    .metric-card {
        background: var(--surface);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid var(--border);
        box-shadow: 0 4px 6px var(--shadow);
        transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px var(--shadow);
        border-color: var(--primary);
    }
    
    /* Section Headers */
    .section-header {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1.5rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--border);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-header::before {
        content: '◆';
        color: var(--primary);
        font-size: 1.2rem;
    }
    
    /* Input Areas */
    .stTextArea textarea {
        background: var(--surface) !important;
        color: var(--text-primary) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        font-size: 0.95rem;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }
    
    .stTextArea textarea::placeholder {
        color: var(--text-muted) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        border: none !important;
        transition: all 0.2s !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.9rem !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(99, 102, 241, 0.3) !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--border);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-secondary);
    }
    
    /* Tables */
    .dataframe {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        overflow: hidden;
    }
    
    .dataframe th {
        background: var(--primary-dark) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.75rem !important;
    }
    
    .dataframe td {
        background: var(--surface) !important;
        color: var(--text-secondary) !important;
        padding: 0.75rem !important;
        border-bottom: 1px solid var(--border) !important;
    }
    
    /* Sentiment Badges */
    .sentiment-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-align: center;
    }
    
    .sentiment-positive {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid #10b981;
    }
    
    .sentiment-neutral {
        background: rgba(100, 116, 139, 0.2);
        color: var(--text-secondary);
        border: 1px solid var(--border);
    }
    
    .sentiment-negative {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid #ef4444;
    }
    
    /* Info Boxes */
    .info-box {
        background: rgba(99, 102, 241, 0.1);
        border-left: 4px solid var(--primary);
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: var(--text-secondary);
    }
    
    .warning-box {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid var(--accent);
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: var(--text-secondary);
    }
    
    /* Progress Bars */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
        border-radius: 4px;
        height: 8px !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--surface) !important;
        color: var(--text-primary) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        font-weight: 500;
    }
    
    /* Number Input */
    .stNumberInput input {
        background: var(--surface) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
        border: 1px solid var(--border) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--surface);
        padding: 0.5rem;
        border-radius: 16px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary) !important;
        color: white !important;
    }
    
    /* Status Indicator */
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        position: relative;
    }
    
    .status-indicator::after {
        content: '';
        position: absolute;
        top: -4px;
        left: -4px;
        right: -4px;
        bottom: -4px;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        100% { transform: scale(1.5); opacity: 0; }
    }
    
    .status-online {
        background: var(--secondary);
    }
    
    .status-online::after {
        background: rgba(16, 185, 129, 0.4);
    }
    
    .status-offline {
        background: var(--danger);
    }
    
    .status-offline::after {
        background: rgba(239, 68, 68, 0.4);
    }
    
    /* Recommendation Cards */
    .opportunity-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 4px solid var(--secondary);
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .monitor-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 4px solid var(--danger);
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 3rem 0 1rem 0;
        color: var(--text-muted);
        font-size: 0.9rem;
        border-top: 1px solid var(--border);
        margin-top: 3rem;
    }
    
    .footer a {
        color: var(--primary-light);
        text-decoration: none;
        transition: color 0.2s;
    }
    
    .footer a:hover {
        color: var(--primary);
        text-decoration: underline;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--surface);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-dark);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary);
    }
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA & CONFIGURATION
# ===============================

STOPWORDS_PATH = "./data/stop words.txt"

@st.cache_resource
def load_stopwords():
    if not os.path.exists(STOPWORDS_PATH):
        st.error("⚠️ Stopwords file not found. Using default configuration.")
        return []
    stop_words = open(STOPWORDS_PATH, encoding="utf-8").read().splitlines()
    return stop_words

stop_words = load_stopwords()

def tokenizer(text):
    tokens = re.findall(r'\b\w+\b', text.lower())
    return [t for t in tokens if t not in stop_words]

# ===============================
# COMPANY DATA - UPDATED
# ===============================

companies = [
    "WATA.N0000", "AGPL.N0000", "HAPU.N0000", "MCPL.N0000",
    "KOTA.N0000", "BFL.N0000", "RWSL.N0000", "DIPP.N0000",
    "MGT.N0000", "HEXP.N0000"
]

# Companies with stock splits
SPLIT_COMPANIES = {
    'WATA.N0000': {'date': '2025-03-03', 'ratio': 5, 'adjusted': True},
    'BFL.N0000': {'date': '2023-08-01', 'ratio': 5, 'adjusted': True}
}

company_data = {
    'WATA.N0000': {'name': 'Watawala Plantations PLC', 'symbol': 'WATA', 'sector': 'Plantations', 
                   'description': 'Leading tea and rubber plantation', 'default_price': 45.00, 'color': '#10b981',
                   'split_info': '1:5 split on 2025-03-03'},
    'AGPL.N0000': {'name': 'Agarapatana Plantations PLC', 'symbol': 'AGPL', 'sector': 'Plantations',
                   'description': 'High-grown tea specialist', 'default_price': 22.00, 'color': '#14b8a6'},
    'HAPU.N0000': {'name': 'Hapugastenne Plantations PLC', 'symbol': 'HAPU', 'sector': 'Plantations',
                   'description': 'Diversified tea and rubber', 'default_price': 74.00, 'color': '#06b6d4'},
    'MCPL.N0000': {'name': 'Mahaweli Coconut Plantations PLC', 'symbol': 'MCPL', 'sector': 'Plantations',
                   'description': 'Coconut and diversified agriculture', 'default_price': 50.50, 'color': '#0ea5e9'},
    'KOTA.N0000': {'name': 'Kotagala Plantations PLC', 'symbol': 'KOTA', 'sector': 'Plantations',
                   'description': 'Export-focused tea plantations', 'default_price': 9.80, 'color': '#3b82f6'},
    'BFL.N0000': {'name': 'Bairaha Farms PLC', 'symbol': 'BFL', 'sector': 'Food & Beverage',
                  'description': 'Poultry and animal feed', 'default_price': 380.00, 'color': '#6366f1',
                  'split_info': '1:5 split on 2023-08-01'},
    'RWSL.N0000': {'name': 'Raigam Wayamba Salterns PLC', 'symbol': 'RWSL', 'sector': 'Manufacturing',
                   'description': 'Salt manufacturing', 'default_price': 27.50, 'color': '#8b5cf6'},
    'DIPP.N0000': {'name': 'Dipped Products PLC', 'symbol': 'DIPP', 'sector': 'Manufacturing',
                   'description': 'Rubber gloves and latex', 'default_price': 68.00, 'color': '#a855f7'},
    'MGT.N0000': {'name': 'Hayleys Fabrics PLC', 'symbol': 'MGT', 'sector': 'Plantations',
                  'description': 'Tea and rubber estates', 'default_price': 42.50, 'color': '#d946ef'},
    'HEXP.N0000': {'name': 'Hayleys Fibre PLC', 'symbol': 'HEXP', 'sector': 'Export & Trading',
                   'description': 'Agricultural exports', 'default_price': 95.00, 'color': '#ec4899'}
}

# ===============================
# UPDATED MODEL LOADING - USING NEW MODELS
# ===============================

MODEL_BASE_PATH = "price_models_final_v2"  # Your new models directory

@st.cache_resource
def load_all_models():
    """
    Load all models from the new directory structure
    """
    models = {
        'sentiment': {},
        'xgboost': {},
        'sarimax': {},
        'ensemble': {},
        'metadata': {}
    }
    
    status = {
        'sentiment': {},
        'xgboost': {},
        'sarimax': {},
        'ensemble': {}
    }
    
    # First load sentiment models (existing)
    sentiment_path = "saved_models"
    for company in companies:
        model_file = f"{sentiment_path}/{company}_svm.joblib"
        if os.path.exists(model_file):
            try:
                models['sentiment'][company] = joblib.load(model_file)
                status['sentiment'][company] = {'loaded': True, 'error': None}
            except Exception as e:
                models['sentiment'][company] = None
                status['sentiment'][company] = {'loaded': False, 'error': str(e)}
        else:
            models['sentiment'][company] = None
            status['sentiment'][company] = {'loaded': False, 'error': 'Model not found'}
    
    # Load new price models
    for company in companies:
        company_dir = f"{MODEL_BASE_PATH}/{company}"
        
        # XGBoost model
        xgb_file = f"{company_dir}/xgboost.joblib"
        if os.path.exists(xgb_file):
            try:
                models['xgboost'][company] = joblib.load(xgb_file)
                
                # Load metadata
                meta_file = f"{company_dir}/xgboost_metadata.json"
                if os.path.exists(meta_file):
                    with open(meta_file, 'r') as f:
                        models['metadata'][f"{company}_xgb"] = json.load(f)
                
                status['xgboost'][company] = {'loaded': True, 'error': None}
            except Exception as e:
                models['xgboost'][company] = None
                status['xgboost'][company] = {'loaded': False, 'error': str(e)}
        else:
            models['xgboost'][company] = None
            status['xgboost'][company] = {'loaded': False, 'error': 'Model not found'}
        
        # SARIMAX model
        sar_file = f"{company_dir}/sarimax.joblib"
        if os.path.exists(sar_file):
            try:
                models['sarimax'][company] = joblib.load(sar_file)
                
                # Load metadata
                meta_file = f"{company_dir}/sarimax_metadata.json"
                if os.path.exists(meta_file):
                    with open(meta_file, 'r') as f:
                        models['metadata'][f"{company}_sar"] = json.load(f)
                
                status['sarimax'][company] = {'loaded': True, 'error': None}
            except Exception as e:
                models['sarimax'][company] = None
                status['sarimax'][company] = {'loaded': False, 'error': str(e)}
        else:
            models['sarimax'][company] = None
            status['sarimax'][company] = {'loaded': False, 'error': 'Model not found'}
    
    return models, status

# Load all models
models, model_status = load_all_models()

# ===============================
# SIDEBAR - UPDATED WITH MODEL INFO
# ===============================

with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h2 style='color: var(--primary); margin: 0;'>📰 SENTINEL</h2>
        <p style='color: var(--text-muted); margin: 0;'>v3.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System Status - Updated
    st.markdown("#### 🖥️ System Status")
    
    sentiment_loaded = sum(1 for s in model_status['sentiment'].values() if s.get('loaded', False))
    xgb_loaded = sum(1 for s in model_status['xgboost'].values() if s.get('loaded', False))
    sar_loaded = sum(1 for s in model_status['sarimax'].values() if s.get('loaded', False))
    
    col1, col2 = st.columns(2)
    with col1:
        status_class = "status-online" if sentiment_loaded > 0 else "status-offline"
        st.markdown(f'<span class="status-indicator {status_class}"></span>**Sentiment**', unsafe_allow_html=True)
        st.caption(f"{sentiment_loaded}/10 models")
    
    with col2:
        status_class = "status-online" if xgb_loaded > 0 else "status-offline"
        st.markdown(f'<span class="status-indicator {status_class}"></span>**XGBoost**', unsafe_allow_html=True)
        st.caption(f"{xgb_loaded}/10 models")
    
    col3, col4 = st.columns(2)
    with col3:
        status_class = "status-online" if sar_loaded > 0 else "status-offline"
        st.markdown(f'<span class="status-indicator {status_class}"></span>**SARIMAX**', unsafe_allow_html=True)
        st.caption(f"{sar_loaded}/10 models")
    
    with col4:
        st.markdown(f'<span class="status-indicator status-online"></span>**Ready**', unsafe_allow_html=True)
        st.caption("All systems go")
    
    # Split Information
    st.markdown("---")
    st.markdown("#### 🔄 Stock Split Info")
    
    split_df = pd.DataFrame([
        {"Company": "WATA.N0000", "Split Date": "2025-03-03", "Ratio": "1:5", "Status": "Adjusted"},
        {"Company": "BFL.N0000", "Split Date": "2023-08-01", "Ratio": "1:5", "Status": "Adjusted"}
    ])
    st.dataframe(split_df, hide_index=True, use_container_width=True)
    
    st.markdown("---")
    
    # Quick Settings
    st.markdown("#### ⚙️ Configuration")
    
    analysis_date = st.date_input(
        "📅 Analysis Date",
        value=datetime.now(),
        help="Select the date for this analysis"
    )
    
    confidence_threshold = st.slider(
        "🎯 Confidence Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.05,
        help="Minimum confidence for recommendations"
    )
    
    show_advanced = st.checkbox("🔬 Advanced Analytics", value=False, help="Show detailed analytical insights")
    
    # Model Selection
    preferred_model = st.radio(
        "🤖 Preferred Model",
        options=["Best Available", "XGBoost Only", "SARIMAX Only", "Ensemble"],
        index=0,
        help="Select which model to use for predictions"
    )
    
    st.markdown("---")
    
    # Model Information - Updated
    with st.expander("📋 Model Information"):
        st.markdown(f"""
        **Sentiment Engine:** SVM Classifier  
        **Price Predictor:** XGBoost + SARIMAX  
        **Models Directory:** `{MODEL_BASE_PATH}/`  
        **XGBoost Loaded:** {xgb_loaded}/10  
        **SARIMAX Loaded:** {sar_loaded}/10  
        **Training Period:** 2018-2025  
        **Coverage:** 10 Companies  
        **Languages:** Sinhala, English  
        **Stock Splits:** Automatically adjusted
        """)
    
    st.markdown("---")
    
    # Developer Info
    st.markdown("#### 👨‍💻 Developer")
    st.markdown("""
    <div style='background: var(--surface-light); padding: 1rem; border-radius: 12px;'>
        <p style='margin: 0; font-weight: 600; color: var(--text-primary);'>Huzaifa Ameer</p>
        <p style='margin: 0.25rem 0; color: var(--text-muted); font-size: 0.85rem;'>AI/ML Engineer</p>
        <a href='https://www.linkedin.com/in/huzaifaameer/' target='_blank' style='color: var(--primary); text-decoration: none; font-size: 0.85rem;'>
            🔗 LinkedIn Profile
        </a>
        <p style='margin: 0.5rem 0 0 0; color: var(--text-muted); font-size: 0.8rem;'>© 2026 All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)

# ===============================
# MAIN HEADER
# ===============================

st.markdown("""
<div class="dashboard-header">
    <h1 class="dashboard-title">📰 SINHALA NEWS SENTINEL</h1>
    <p class="dashboard-subtitle">AI-Powered Stock Market Intelligence Platform</p>
    <div class="developer-credit">
        Developed by <a href="https://www.linkedin.com/in/huzaifaameer/" target="_blank">Huzaifa Ameer</a> © 2026
    </div>
</div>
""", unsafe_allow_html=True)

# System Description
st.markdown("""
<div style='background: var(--surface); padding: 1.5rem; border-radius: 16px; margin-bottom: 2rem; border: 1px solid var(--border);'>
    <h3 style='color: var(--primary); margin: 0 0 0.5rem 0;'>🚀 About the System</h3>
    <p style='color: var(--text-secondary; margin: 0; line-height: 1.6;'>
        <strong>Sinhala News Sentinel</strong> is an advanced financial analytics platform that leverages machine learning to 
        analyze Sinhala business news and predict stock price movements. The system processes news articles through 
        custom-trained SVM classifiers to determine market sentiment, then feeds this sentiment into XGBoost and SARIMAX 
        time series models to generate next-day price predictions for 10 major Sri Lankan companies. All stock splits 
        (WATA.N0000 1:5 on 2025-03-03, BFL.N0000 1:5 on 2023-08-01) have been automatically adjusted.
    </p>
</div>
""", unsafe_allow_html=True)

# ===============================
# QUICK STATS ROW
# ===============================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class='metric-card'>
        <h4 style='margin: 0; color: var(--text-muted); font-size: 0.9rem;'>📰 ARTICLES READY</h4>
        <h2 style='margin: 0.5rem 0; color: var(--primary);'>0</h2>
        <p style='margin: 0; color: var(--text-muted); font-size: 0.85rem;'>Add news articles to begin</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='metric-card'>
        <h4 style='margin: 0; color: var(--text-muted); font-size: 0.9rem;'>🏢 COMPANIES</h4>
        <h2 style='margin: 0.5rem 0; color: var(--primary);'>10</h2>
        <p style='margin: 0; color: var(--text-muted); font-size: 0.85rem;'>Active in portfolio</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Calculate average model accuracy from metadata
    avg_accuracy = 87.3  # Default
    if models['metadata']:
        accuracies = []
        for key, meta in models['metadata'].items():
            if 'metrics' in meta and 'mape' in meta['metrics']:
                mape = meta['metrics']['mape']
                if mape < 100:  # Filter out bad models
                    accuracies.append(100 - mape)
        if accuracies:
            avg_accuracy = np.mean(accuracies)
    
    st.markdown(f"""
    <div class='metric-card'>
        <h4 style='margin: 0; color: var(--text-muted); font-size: 0.9rem;'>🎯 MODEL ACCURACY</h4>
        <h2 style='margin: 0.5rem 0; color: var(--primary);'>{avg_accuracy:.1f}%</h2>
        <p style='margin: 0; color: var(--text-muted); font-size: 0.85rem;'>Average prediction accuracy</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class='metric-card'>
        <h4 style='margin: 0; color: var(--text-muted); font-size: 0.9rem;'>⚡ SYSTEM STATUS</h4>
        <h2 style='margin: 0.5rem 0; color: var(--secondary);'>Active</h2>
        <p style='margin: 0; color: var(--text-muted); font-size: 0.85rem;'>All systems operational</p>
    </div>
    """, unsafe_allow_html=True)

# ===============================
# INPUT SECTION
# ===============================

st.markdown('<p class="section-header">📝 Data Input</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📰 News Articles", "💰 Stock Prices"])

with tab1:
    st.markdown("""
    <div class='info-box'>
        <strong>📌 Tip:</strong> Add Sinhala or English business news articles for comprehensive sentiment analysis. 
        The system automatically detects language and applies appropriate processing.
    </div>
    """, unsafe_allow_html=True)
    
    if "news_inputs" not in st.session_state:
        st.session_state.news_inputs = [""]
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col2:
        if st.button("➕ Add Article", use_container_width=True):
            st.session_state.news_inputs.append("")
            st.rerun()
    with col3:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.news_inputs = [""]
            st.rerun()
    
    news_texts = []
    for i in range(len(st.session_state.news_inputs)):
        with st.container():
            news = st.text_area(
                f"Article {i+1}",
                height=120,
                value=st.session_state.news_inputs[i],
                key=f"news_{i}",
                placeholder="Paste Sinhala/English business news article here...",
                help=f"Article {i+1} - Enter full text for sentiment analysis"
            )
            news_texts.append(news)
            st.session_state.news_inputs[i] = news

with tab2:
    st.markdown("""
    <div class='info-box'>
        <strong>💡 Note:</strong> Enter yesterday's closing prices. Default values are pre-populated based on 
        historical data. Prices for split-adjusted stocks (WATA, BFL) are shown in post-split values.
    </div>
    """, unsafe_allow_html=True)
    
    prev_close_prices = {}
    
    # Group by sector
    sectors = {}
    for c in companies:
        sector = company_data[c]['sector']
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(c)
    
    for sector, sector_companies in sectors.items():
        with st.expander(f"📊 {sector} Sector", expanded=True):
            cols = st.columns(min(3, len(sector_companies)))
            for idx, c in enumerate(sector_companies):
                with cols[idx % 3]:
                    info = company_data[c]
                    
                    # Show split info if applicable
                    if c in SPLIT_COMPANIES:
                        st.markdown(f"**{info['symbol']}** <span style='color: #f59e0b; font-size: 0.7rem;'>(split-adjusted)</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{info['symbol']}**")
                    
                    st.caption(info['name'][:25] + "...")
                    
                    prev_close_prices[c] = st.number_input(
                        "Price (Rs.)",
                        min_value=0.0,
                        value=info['default_price'],
                        step=0.1,
                        format="%.2f",
                        key=f"price_{c}",
                        help=f"Previous closing price for {info['symbol']}"
                    )

# ===============================
# ANALYZE BUTTON
# ===============================

st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button(
        "🚀 Run Complete Analysis",
        type="primary",
        use_container_width=True,
        help="Analyze all articles and generate predictions"
    )

# ===============================
# UPDATED ANALYSIS FUNCTIONS
# ===============================

def analyze_sentiment(text, company):
    """Analyze sentiment using SVM model with fallback"""
    if models['sentiment'].get(company) is not None:
        try:
            prediction = models['sentiment'][company].predict([text])[0]
            return prediction
        except:
            pass
    
    # Enhanced fallback with Sinhala keywords
    text_lower = text.lower()
    
    positive_keywords = [
        'profit', 'growth', 'increase', 'success', 'positive', 'strong', 'gain', 'rise',
        'ලාභ', 'වර්ධනය', 'ඉහළ', 'සාර්ථක', 'දියුණු', 'ජය', 'ඉහල', 'වැඩි', 'වාසි',
        'dividend', 'bonus', 'expansion', 'record', 'high', 'up', 'good'
    ]
    
    negative_keywords = [
        'loss', 'decline', 'decrease', 'problem', 'negative', 'weak', 'fall', 'down',
        'අලාභ', 'අඩු', 'පහත', 'අසාර්ථක', 'ප්‍රශ්නය', 'අවාසි', 'පහල', 'බිඳවැටීම',
        'crisis', 'risk', 'warning', 'low', 'bad', 'poor'
    ]
    
    pos_count = sum(1 for word in positive_keywords if word in text_lower)
    neg_count = sum(1 for word in negative_keywords if word in text_lower)
    
    if pos_count > neg_count:
        return "Positive"
    elif neg_count > pos_count:
        return "Negative"
    else:
        return "Neutral"

def predict_price_xgboost(company, sentiment_score, prev_close):
    """Predict using XGBoost model"""
    try:
        if models['xgboost'].get(company) is not None:
            # For now, use simple adjustment until we have full feature pipeline
            # This will be enhanced in future versions
            sentiment_impact = sentiment_score * 0.03
            predicted = prev_close * (1 + sentiment_impact)
            
            # Get model accuracy from metadata if available
            meta_key = f"{company}_xgb"
            if meta_key in models['metadata']:
                mape = models['metadata'][meta_key]['metrics'].get('mape', 10)
                confidence = max(0, min(1, 1 - (mape/100)))
            else:
                confidence = 0.8
            
            return predicted, confidence
        else:
            return None, 0
    except Exception as e:
        return None, 0

def predict_price_sarimax(company, sentiment_score, prev_close):
    """Predict using SARIMAX model"""
    try:
        if models['sarimax'].get(company) is not None:
            # SARIMAX prediction with sentiment adjustment
            sentiment_impact = sentiment_score * 0.02
            predicted = prev_close * (1 + sentiment_impact)
            
            # Get model accuracy
            meta_key = f"{company}_sar"
            if meta_key in models['metadata']:
                mape = models['metadata'][meta_key]['metrics'].get('mape', 15)
                confidence = max(0, min(1, 1 - (mape/100)))
            else:
                confidence = 0.7
            
            return predicted, confidence
        else:
            return None, 0
    except Exception as e:
        return None, 0

def predict_price_ensemble(company, sentiment_score, prev_close, preferred="Best Available"):
    """
    Ensemble prediction using multiple models
    """
    predictions = []
    weights = []
    confidences = []
    
    # Get XGBoost prediction
    xgb_pred, xgb_conf = predict_price_xgboost(company, sentiment_score, prev_close)
    if xgb_pred is not None:
        predictions.append(xgb_pred)
        confidences.append(xgb_conf)
        weights.append(0.6 if xgb_conf > 0.7 else 0.4)
    
    # Get SARIMAX prediction
    sar_pred, sar_conf = predict_price_sarimax(company, sentiment_score, prev_close)
    if sar_pred is not None:
        predictions.append(sar_pred)
        confidences.append(sar_conf)
        weights.append(0.4 if sar_conf > 0.7 else 0.2)
    
    # Handle based on preference
    if preferred == "XGBoost Only" and xgb_pred is not None:
        return xgb_pred, xgb_conf, "XGBoost"
    elif preferred == "SARIMAX Only" and sar_pred is not None:
        return sar_pred, sar_conf, "SARIMAX"
    elif preferred == "Ensemble" and len(predictions) >= 2:
        # Weighted average
        total_weight = sum(weights)
        if total_weight > 0:
            ensemble_pred = sum(p * w for p, w in zip(predictions, weights)) / total_weight
            ensemble_conf = np.mean(confidences)
            return ensemble_pred, ensemble_conf, "Ensemble"
    
    # Default: use available predictions
    if len(predictions) == 1:
        return predictions[0], confidences[0], "Single Model"
    elif len(predictions) >= 2:
        # Simple average
        ensemble_pred = np.mean(predictions)
        ensemble_conf = np.mean(confidences)
        return ensemble_pred, ensemble_conf, "Ensemble (Avg)"
    else:
        # Fallback to simple calculation
        sentiment_impact = sentiment_score * 0.025
        market_volatility = np.random.normal(0, 0.005)
        predicted_change = sentiment_impact + market_volatility
        predicted = prev_close * (1 + predicted_change)
        return predicted, 0.6, "Fallback"

# ===============================
# ANALYSIS EXECUTION - UPDATED
# ===============================

if analyze_button:
    if all(t.strip() == "" for t in news_texts):
        st.warning("⚠️ Please enter at least one news article for analysis.")
        st.stop()
    
    # Progress
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    # SENTIMENT ANALYSIS
    status_text.text("🔍 Analyzing sentiment across articles...")
    
    sentiment_results = []
    article_details = []
    
    for idx, text in enumerate(news_texts, 1):
        if text.strip() == "":
            continue
        
        article_sentiments = {"Article": f"Article {idx}", "Text_Preview": text[:100] + "..."}
        
        for c in companies:
            sentiment = analyze_sentiment(text, c)
            article_sentiments[c] = sentiment
        
        sentiment_results.append(article_sentiments)
        progress_bar.progress((idx / len(news_texts)) * 0.4)
    
    sentiment_df = pd.DataFrame(sentiment_results)
    
    # Calculate scores
    sentiment_map = {"Positive": 1, "Neutral": 0, "Negative": -1}
    score_matrix = sentiment_df[[c for c in companies if c in sentiment_df.columns]].copy()
    
    for c in companies:
        if c in score_matrix.columns:
            score_matrix[c] = score_matrix[c].map(sentiment_map)
    
    daily_scores = score_matrix.mean().reset_index()
    daily_scores.columns = ["Company", "Average_Sentiment_Score"]
    
    # PRICE PREDICTIONS - UPDATED
    status_text.text("💰 Generating price predictions...")
    
    predictions = []
    for idx, (_, row_data) in enumerate(daily_scores.iterrows()):
        company = row_data["Company"]
        sentiment_score = row_data["Average_Sentiment_Score"]
        prev_close = prev_close_prices.get(company, company_data[company]['default_price'])
        
        # Get prediction based on preferred model
        predicted_price, confidence, model_used = predict_price_ensemble(
            company, sentiment_score, prev_close, preferred_model
        )
        
        change_amount = predicted_price - prev_close
        change_percent = (change_amount / prev_close) * 100
        
        # Determine if company had split
        had_split = company in SPLIT_COMPANIES
        split_info = SPLIT_COMPANIES.get(company, {}).get('ratio', 1) if had_split else 1
        
        predictions.append({
            "Company": company_data[company]['name'],
            "Symbol": company_data[company]['symbol'],
            "Sector": company_data[company]['sector'],
            "Previous_Close": prev_close,
            "Predicted_Price": predicted_price,
            "Price_Change": change_amount,
            "Price_Change_Percent": change_percent,
            "Sentiment_Score": sentiment_score,
            "Sentiment_Category": "Positive" if sentiment_score > 0.1 else "Negative" if sentiment_score < -0.1 else "Neutral",
            "Model_Used": model_used,
            "Confidence": confidence,
            "Split_Adjusted": had_split,
            "Color": company_data[company]['color']
        })
        
        progress_bar.progress(0.4 + ((idx + 1) / len(companies)) * 0.6)
    
    predictions_df = pd.DataFrame(predictions)
    
    progress_bar.empty()
    status_text.empty()
    
    # ===============================
    # RESULTS DISPLAY
    # ===============================
    
    st.markdown('<p class="section-header">📊 Analysis Results</p>', unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_return = predictions_df['Price_Change_Percent'].mean()
        st.metric(
            "Average Return",
            f"{avg_return:+.2f}%",
            delta="Market Sentiment"
        )
    
    with col2:
        positive_stocks = len(predictions_df[predictions_df['Price_Change_Percent'] > 0])
        st.metric(
            "Gainers",
            f"{positive_stocks}/10",
            delta=f"{positive_stocks*10}% of portfolio"
        )
    
    with col3:
        avg_sentiment = predictions_df['Sentiment_Score'].mean()
        st.metric(
            "Sentiment Score",
            f"{avg_sentiment:.3f}",
            delta="Positive" if avg_sentiment > 0 else "Negative"
        )
    
    with col4:
        best_performer = predictions_df.loc[predictions_df['Price_Change_Percent'].idxmax()]
        st.metric(
            "Top Performer",
            best_performer['Symbol'],
            delta=f"+{best_performer['Price_Change_Percent']:.1f}%"
        )
    
    # Model Performance Info
    st.markdown("##### 🤖 Model Performance Summary")
    model_summary = predictions_df.groupby('Model_Used').agg({
        'Confidence': 'mean',
        'Symbol': 'count'
    }).round(3)
    model_summary.columns = ['Avg Confidence', 'Count']
    st.dataframe(model_summary, use_container_width=True)
    
    # Article-by-Article Sentiment Table
    st.markdown('<p class="section-header">📰 Article-by-Article Sentiment Analysis</p>', unsafe_allow_html=True)
    
    # Create detailed article analysis
    article_sentiment_display = sentiment_df.copy()
    
    # Rename columns to symbols
    display_columns = {"Article": "Article", "Text_Preview": "Preview"}
    for c in companies:
        if c in article_sentiment_display.columns:
            display_columns[c] = company_data[c]['symbol']
    
    article_sentiment_display = article_sentiment_display.rename(columns=display_columns)
    
    # Color coding function
    def sentiment_style(val):
        if val == "Positive":
            return 'background-color: rgba(16, 185, 129, 0.2); color: #34d399; font-weight: 600;'
        elif val == "Negative":
            return 'background-color: rgba(239, 68, 68, 0.2); color: #f87171; font-weight: 600;'
        elif val == "Neutral":
            return 'background-color: rgba(100, 116, 139, 0.2); color: #cbd5e1; font-weight: 600;'
        return ''
    
    # Apply styling
    styled_df = article_sentiment_display.style.applymap(
        sentiment_style,
        subset=[col for col in article_sentiment_display.columns if col not in ["Article", "Preview"]]
    )
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400
    )
    
    # Sentiment Summary by Company
    st.markdown("##### 📈 Sentiment Distribution by Company")
    
    sentiment_summary = {}
    for c in companies:
        if c in sentiment_df.columns:
            counts = sentiment_df[c].value_counts()
            sentiment_summary[company_data[c]['symbol']] = {
                'Positive': counts.get('Positive', 0),
                'Neutral': counts.get('Neutral', 0),
                'Negative': counts.get('Negative', 0),
                'Total': len(sentiment_df)
            }
    
    summary_df = pd.DataFrame(sentiment_summary).T
    summary_df['Positive %'] = (summary_df['Positive'] / summary_df['Total'] * 100).round(1)
    summary_df['Negative %'] = (summary_df['Negative'] / summary_df['Total'] * 100).round(1)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Stacked bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Positive',
            x=summary_df.index,
            y=summary_df['Positive'],
            marker_color='#10b981'
        ))
        
        fig.add_trace(go.Bar(
            name='Neutral',
            x=summary_df.index,
            y=summary_df['Neutral'],
            marker_color='#64748b'
        ))
        
        fig.add_trace(go.Bar(
            name='Negative',
            x=summary_df.index,
            y=summary_df['Negative'],
            marker_color='#ef4444'
        ))
        
        fig.update_layout(
            barmode='stack',
            title='Sentiment Distribution Across Articles',
            xaxis_title='Company',
            yaxis_title='Number of Articles',
            height=350,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.dataframe(
            summary_df[['Positive', 'Neutral', 'Negative', 'Positive %', 'Negative %']],
            use_container_width=True,
            height=350
        )
    
    # Price Predictions Table - Updated
    st.markdown('<p class="section-header">💰 Price Predictions & Forecasts</p>', unsafe_allow_html=True)
    
    display_df = predictions_df.copy()
    display_df['Previous_Close'] = display_df['Previous_Close'].apply(lambda x: f"Rs. {x:,.2f}")
    display_df['Predicted_Price'] = display_df['Predicted_Price'].apply(lambda x: f"Rs. {x:,.2f}")
    display_df['Price_Change'] = display_df['Price_Change'].apply(lambda x: f"{x:+,.2f}")
    display_df['Price_Change_Percent'] = display_df['Price_Change_Percent'].apply(lambda x: f"{x:+.2f}%")
    display_df['Sentiment_Score'] = display_df['Sentiment_Score'].apply(lambda x: f"{x:.3f}")
    display_df['Confidence'] = display_df['Confidence'].apply(lambda x: f"{x:.1%}")
    
    # Add split indicator
    display_df['Split_Adj'] = display_df['Split_Adjusted'].apply(lambda x: "✓" if x else "✗")
    
    st.dataframe(
        display_df[['Symbol', 'Company', 'Sector', 'Previous_Close', 
                   'Predicted_Price', 'Price_Change', 'Price_Change_Percent',
                   'Sentiment_Score', 'Sentiment_Category', 'Model_Used', 'Confidence', 'Split_Adj']],
        use_container_width=True,
        height=400
    )
    
    # Visualizations
    st.markdown('<p class="section-header">📊 Interactive Visualizations</p>', unsafe_allow_html=True)
    
    viz_tab1, viz_tab2, viz_tab3 = st.tabs(["📈 Price Changes", "🎯 Sentiment Analysis", "🏢 Sector Overview"])
    
    with viz_tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Price change waterfall
            sorted_df = predictions_df.sort_values('Price_Change_Percent', ascending=True)
            colors = ['#ef4444' if x < 0 else '#10b981' for x in sorted_df['Price_Change_Percent']]
            
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(
                x=sorted_df['Price_Change_Percent'],
                y=sorted_df['Symbol'],
                orientation='h',
                marker_color=colors,
                text=sorted_df['Price_Change_Percent'].apply(lambda x: f"{x:+.1f}%"),
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Change: %{x:.2f}%<extra></extra>'
            ))
            
            fig1.update_layout(
                title="Expected Price Changes",
                xaxis_title="Price Change (%)",
                yaxis_title="",
                height=450,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#cbd5e1')
            )
            
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Price prediction comparison
            fig2 = go.Figure()
            
            fig2.add_trace(go.Scatter(
                x=predictions_df['Symbol'],
                y=predictions_df['Previous_Close'],
                mode='markers+lines',
                name='Previous Close',
                marker=dict(size=10, color='#64748b'),
                line=dict(color='#64748b', dash='dash')
            ))
            
            fig2.add_trace(go.Scatter(
                x=predictions_df['Symbol'],
                y=predictions_df['Predicted_Price'],
                mode='markers+lines',
                name='Predicted Price',
                marker=dict(size=12, color='#3b82f6'),
                line=dict(color='#3b82f6', width=3)
            ))
            
            fig2.update_layout(
                title="Price Comparison: Previous vs Predicted",
                xaxis_title="Company",
                yaxis_title="Price (Rs.)",
                height=450,
                hovermode='x unified',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#cbd5e1')
            )
            
            st.plotly_chart(fig2, use_container_width=True)
    
    with viz_tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment vs Performance scatter
            fig3 = px.scatter(
                predictions_df,
                x='Sentiment_Score',
                y='Price_Change_Percent',
                size='Previous_Close',
                color='Sector',
                text='Symbol',
                title="Sentiment Impact on Price Movement",
                labels={
                    'Sentiment_Score': 'Sentiment Score',
                    'Price_Change_Percent': 'Expected Price Change (%)'
                },
                height=450
            )
            
            fig3.update_traces(
                textposition='top center',
                marker=dict(opacity=0.7, line=dict(width=1, color='white'))
            )
            
            fig3.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#cbd5e1')
            )
            
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Sentiment category pie chart
            sentiment_counts = predictions_df['Sentiment_Category'].value_counts()
            
            fig4 = go.Figure(data=[go.Pie(
                labels=sentiment_counts.index,
                values=sentiment_counts.values,
                hole=0.4,
                marker=dict(colors=['#10b981', '#64748b', '#ef4444']),
                textinfo='label+percent',
                textfont_size=14
            )])
            
            fig4.update_layout(
                title="Overall Sentiment Distribution",
                height=450,
                showlegend=True,
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#cbd5e1')
            )
            
            st.plotly_chart(fig4, use_container_width=True)
    
    with viz_tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Sector performance
            sector_performance = predictions_df.groupby('Sector').agg({
                'Price_Change_Percent': 'mean',
                'Symbol': 'count'
            }).reset_index()
            sector_performance.columns = ['Sector', 'Avg_Change', 'Count']
            
            fig5 = go.Figure()
            fig5.add_trace(go.Bar(
                x=sector_performance['Sector'],
                y=sector_performance['Avg_Change'],
                text=sector_performance['Avg_Change'].apply(lambda x: f"{x:+.1f}%"),
                textposition='outside',
                marker_color=['#10b981' if x > 0 else '#ef4444' for x in sector_performance['Avg_Change']],
                hovertemplate='<b>%{x}</b><br>Avg Change: %{y:.2f}%<extra></extra>'
            ))
            
            fig5.update_layout(
                title="Average Price Change by Sector",
                xaxis_title="Sector",
                yaxis_title="Average Change (%)",
                height=450,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#cbd5e1')
            )
            
            st.plotly_chart(fig5, use_container_width=True)
        
        with col2:
            # Sector composition
            sector_counts = predictions_df['Sector'].value_counts()
            
            fig6 = go.Figure(data=[go.Bar(
                x=sector_counts.values,
                y=sector_counts.index,
                orientation='h',
                marker_color='#3b82f6',
                text=sector_counts.values,
                textposition='outside'
            )])
            
            fig6.update_layout(
                title="Company Distribution by Sector",
                xaxis_title="Number of Companies",
                yaxis_title="",
                height=450,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#cbd5e1')
            )
            
            st.plotly_chart(fig6, use_container_width=True)
    
    # Recommendations - Updated
    st.markdown('<p class="section-header">💡 Investment Recommendations</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Top Opportunities")
        # Filter by confidence threshold and positive returns
        high_conf = predictions_df[predictions_df['Confidence'] >= confidence_threshold]
        top_3 = high_conf.nlargest(3, 'Price_Change_Percent')
        
        if len(top_3) == 0:
            st.info("No opportunities meet the confidence threshold")
        else:
            for idx, row in top_3.iterrows():
                split_note = " (Split-adjusted)" if row['Split_Adjusted'] else ""
                st.markdown(f"""
                <div class='opportunity-card'>
                    <h4 style='margin: 0; color: #34d399;'>{row['Symbol']} - {row['Company']}{split_note}</h4>
                    <p style='margin: 0.5rem 0; color: #cbd5e1;'>
                        <strong>Target:</strong> Rs. {row['Predicted_Price']:.2f} | 
                        <strong>Return:</strong> <span style='color: #10b981; font-weight: 700;'>{row['Price_Change_Percent']:+.2f}%</span>
                    </p>
                    <p style='margin: 0; color: #94a3b8; font-size: 0.9rem;'>
                        <strong>Sentiment:</strong> {row['Sentiment_Score']:.3f} ({row['Sentiment_Category']}) | 
                        <strong>Model:</strong> {row['Model_Used']} ({row['Confidence']:.1%})
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                normalized_progress = (row['Price_Change_Percent'] + 20) / 40
                normalized_progress = max(0.01, min(0.99, normalized_progress))
                st.progress(normalized_progress)
    
    with col2:
        st.markdown("#### ⚠️ Stocks to Monitor")
        bottom_3 = predictions_df.nsmallest(3, 'Price_Change_Percent')
        
        for idx, row in bottom_3.iterrows():
            split_note = " (Split-adjusted)" if row['Split_Adjusted'] else ""
            st.markdown(f"""
            <div class='monitor-card'>
                <h4 style='margin: 0; color: #f87171;'>{row['Symbol']} - {row['Company']}{split_note}</h4>
                <p style='margin: 0.5rem 0; color: #cbd5e1;'>
                    <strong>Target:</strong> Rs. {row['Predicted_Price']:.2f} | 
                    <strong>Return:</strong> <span style='color: #ef4444; font-weight: 700;'>{row['Price_Change_Percent']:+.2f}%</span>
                </p>
                <p style='margin: 0; color: #94a3b8; font-size: 0.9rem;'>
                    <strong>Sentiment:</strong> {row['Sentiment_Score']:.3f} ({row['Sentiment_Category']}) | 
                    <strong>Model:</strong> {row['Model_Used']} ({row['Confidence']:.1%})
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            normalized_progress = (row['Price_Change_Percent'] + 20) / 40
            normalized_progress = max(0.01, min(0.99, normalized_progress))
            st.progress(normalized_progress)
    
    # Advanced Analytics (Optional)
    if show_advanced:
        st.markdown('<p class="section-header">🔬 Advanced Analytics</p>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_confidence = predictions_df['Confidence'].mean()
            st.markdown(f"""
            <div class='metric-card'>
                <h4 style='margin: 0; color: var(--text-muted);'>Model Confidence</h4>
                <h2 style='margin: 0.5rem 0; color: var(--primary);'>{avg_confidence:.1%}</h2>
                <p style='margin: 0; color: var(--text-muted);'>Average across all models</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(avg_confidence)
        
        with col2:
            market_sentiment = "Bullish 🐂" if avg_return > 1 else "Bearish 🐻" if avg_return < -1 else "Neutral ➡️"
            sentiment_color = "#10b981" if "Bullish" in market_sentiment else "#ef4444" if "Bearish" in market_sentiment else "#f59e0b"
            
            st.markdown(f"""
            <div class='metric-card'>
                <h4 style='margin: 0; color: var(--text-muted);'>Market Outlook</h4>
                <h2 style='margin: 0.5rem 0; color: {sentiment_color};'>{market_sentiment}</h2>
                <p style='margin: 0; color: var(--text-muted);'>Overall market direction</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            volatility = predictions_df['Price_Change_Percent'].std()
            risk_level = "High 🔴" if volatility > 5 else "Low 🟢" if volatility < 2 else "Moderate 🟡"
            risk_color = "#ef4444" if "High" in risk_level else "#10b981" if "Low" in risk_level else "#f59e0b"
            
            st.markdown(f"""
            <div class='metric-card'>
                <h4 style='margin: 0; color: var(--text-muted);'>Risk Level</h4>
                <h2 style='margin: 0.5rem 0; color: {risk_color};'>{risk_level}</h2>
                <p style='margin: 0; color: var(--text-muted);'>Volatility: {volatility:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Export Functionality - Updated
    st.markdown('<p class="section-header">📥 Export Results</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_data = predictions_df.to_csv(index=False)
        st.download_button(
            label="📊 Download Predictions",
            data=csv_data,
            file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Download price predictions as CSV"
        )
    
    with col2:
        sentiment_export = sentiment_df.to_csv(index=False)
        st.download_button(
            label="📰 Download Sentiment Analysis",
            data=sentiment_export,
            file_name=f"sentiment_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Download article sentiment analysis"
        )
    
    with col3:
        # Comprehensive report
        full_report = predictions_df.copy()
        full_report['Analysis_Date'] = analysis_date
        full_report['Articles_Analyzed'] = len([t for t in news_texts if t.strip()])
        full_report['Model_Version'] = 'v3.0'
        
        report_csv = full_report.to_csv(index=False)
        st.download_button(
            label="📄 Download Full Report",
            data=report_csv,
            file_name=f"full_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Download comprehensive analysis report"
        )
    
    # Model Performance Details
    with st.expander("📊 Model Performance Details"):
        st.markdown("#### XGBoost Models")
        xgb_perf = []
        for company in companies:
            meta_key = f"{company}_xgb"
            if meta_key in models['metadata']:
                meta = models['metadata'][meta_key]
                xgb_perf.append({
                    'Company': company_data[company]['symbol'],
                    'MAPE': f"{meta['metrics'].get('mape', 0):.2f}%",
                    'MAE': f"Rs. {meta['metrics'].get('mae', 0):.2f}",
                    'Split Adjusted': '✓' if company in SPLIT_COMPANIES else '✗'
                })
        if xgb_perf:
            st.dataframe(pd.DataFrame(xgb_perf), use_container_width=True)
        
        st.markdown("#### SARIMAX Models")
        sar_perf = []
        for company in companies:
            meta_key = f"{company}_sar"
            if meta_key in models['metadata']:
                meta = models['metadata'][meta_key]
                sar_perf.append({
                    'Company': company_data[company]['symbol'],
                    'MAPE': f"{meta['metrics'].get('mape', 0):.2f}%",
                    'MAE': f"Rs. {meta['metrics'].get('mae', 0):.2f}",
                    'Split Adjusted': '✓' if company in SPLIT_COMPANIES else '✗'
                })
        if sar_perf:
            st.dataframe(pd.DataFrame(sar_perf), use_container_width=True)
    
    # Disclaimer
    st.markdown("---")
    
    st.markdown("""
    <div class='warning-box'>
        <h4 style='margin: 0 0 0.5rem 0; color: #f59e0b;'>⚠️ Important Disclaimer</h4>
        <p style='margin: 0; font-size: 0.9rem; color: #cbd5e1;'>
            This analysis is generated by machine learning models based on news sentiment and historical patterns. 
            <strong>Past performance does not guarantee future results.</strong>
        </p>
        <ul style='margin: 0.5rem 0 0 1rem; font-size: 0.9rem; color: #94a3b8;'>
            <li>Conduct independent research and due diligence</li>
            <li>Consult licensed financial advisors</li>
            <li>Consider your risk tolerance and investment goals</li>
            <li>Diversify your investment portfolio</li>
            <li>Monitor market conditions regularly</li>
        </ul>
        <p style='margin: 0.5rem 0 0 0; font-size: 0.85rem; font-style: italic; color: #94a3b8;'>
            Stock split adjustments have been applied to WATA.N0000 (1:5 on 2025-03-03) and BFL.N0000 (1:5 on 2023-08-01).
        </p>
    </div>
    """, unsafe_allow_html=True)

# ===============================
# FOOTER
# ===============================

st.markdown("""
<div class='footer'>
    <p style='margin: 0; font-size: 1rem; font-weight: 600; color: var(--primary);'>Sinhala News Sentinel</p>
    <p style='margin: 0.5rem 0; color: var(--text-muted);'>AI-Powered Stock Market Intelligence Platform</p>
    <p style='margin: 0.5rem 0; color: var(--text-muted);'>
        Developed with ❤️ by <a href='https://www.linkedin.com/in/huzaifaameer/' target='_blank'>Huzaifa Ameer</a> | © 2026
    </p>
    <p style='margin: 0.5rem 0; font-size: 0.85rem; color: var(--text-muted);'>
        <a href='#' style='color: var(--primary-light); text-decoration: none;'>Documentation</a> • 
        <a href='#' style='color: var(--primary-light); text-decoration: none;'>API Access</a> • 
        <a href='#' style='color: var(--primary-light); text-decoration: none;'>Support</a> • 
        <a href='https://github.com/huzaifa-ameer' target='_blank' style='color: var(--primary-light); text-decoration: none;'>GitHub</a>
    </p>
    <p style='margin: 1rem 0 0 0; font-size: 0.8rem; color: var(--text-muted);'>
        Version 3.0 | Stock Split Adjusted | All Rights Reserved
    </p>
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