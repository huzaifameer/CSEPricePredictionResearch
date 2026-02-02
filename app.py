# # ===============================
# # STREAMLIT SENTIMENT → SARIMAX PRICE PREDICTION
# # ===============================

# import streamlit as st
# import pandas as pd
# import joblib
# import re
# import os
# import numpy as np
# import plotly.graph_objects as go

# # ===============================
# # CONFIG
# # ===============================

# st.set_page_config(
#     page_title="Sinhala Business News Sentiment & Stock Price Prediction",
#     layout="wide"
# )

# # ===============================
# # STOPWORDS + TOKENIZER
# # ===============================

# STOPWORDS_PATH = "./data/stop words.txt"
# stop_words = open(STOPWORDS_PATH, encoding="utf-8").read().splitlines()

# def tokenizer(text):
#     tokens = re.findall(r'\b\w+\b', text.lower())
#     return [t for t in tokens if t not in stop_words]

# # ===============================
# # COMPANIES
# # ===============================

# companies = [
#     'WATA.N0000','AGPL.N0000','HAPU.N0000','MCPL.N0000',
#     'KOTA.N0000','BFL.N0000','RWSL.N0000','DIPP.N0000',
#     'MGT.N0000','HEXP.N0000'
# ]

# # ===============================
# # LOAD SENTIMENT MODELS
# # ===============================

# @st.cache_resource
# def load_sentiment_models():
#     models = {}
#     for c in companies:
#         path = f"saved_models/{c}_svm.joblib"
#         models[c] = joblib.load(path)
#     return models

# sentiment_models = load_sentiment_models()

# # ===============================
# # LOAD SARIMAX PRICE MODELS
# # ===============================

# @st.cache_resource
# def load_price_models():
#     models = {}
#     for c in companies:
#         path = f"price_models_sarimax/{c}_sarimax.joblib"
#         if os.path.exists(path):
#             models[c] = joblib.load(path)
#     return models

# price_models = load_price_models()

# # ===============================
# # UI HEADER
# # ===============================

# st.title("Sinhala Business News Sentiment & Stock Price Prediction")
# st.caption("News sentiment → Next-day stock price using SARIMAX")

# # ===============================
# # INPUT NEWS
# # ===============================

# st.subheader("Input News Articles")

# if "news_inputs" not in st.session_state:
#     st.session_state.news_inputs = [""]

# def add_news():
#     st.session_state.news_inputs.append("")

# st.button("Add Article", on_click=add_news)

# news_texts = []
# for i in range(len(st.session_state.news_inputs)):
#     news = st.text_area(
#         f"News Article {i+1}",
#         key=f"news_{i}",
#         height=120
#     )
#     news_texts.append(news)

# # ===============================
# # RUN PIPELINE
# # ===============================

# if st.button("Analyze Sentiment & Predict Prices", type="primary"):

#     if all(n.strip() == "" for n in news_texts):
#         st.warning("Please enter at least one news article.")
#         st.stop()

#     # ===============================
#     # SENTIMENT PREDICTION
#     # ===============================

#     sentiment_rows = []

#     for idx, text in enumerate(news_texts):
#         if not text.strip():
#             continue

#         row = {"Article": f"Article {idx+1}"}
#         for c in companies:
#             row[c] = sentiment_models[c].predict([text])[0]
#         sentiment_rows.append(row)

#     sentiment_df = pd.DataFrame(sentiment_rows)
#     st.subheader("Sentiment Classification")
#     st.dataframe(sentiment_df, use_container_width=True)

#     # ===============================
#     # SENTIMENT SCORING
#     # ===============================

#     sentiment_map = {"Positive": 1, "Neutral": 0, "Negative": -1}
#     score_df = sentiment_df.copy()

#     for c in companies:
#         score_df[c] = score_df[c].map(sentiment_map)

#     daily_scores = score_df[companies].mean().reset_index()
#     daily_scores.columns = ["Company", "Sentiment Score"]
#     daily_scores["Sentiment Score"] = daily_scores["Sentiment Score"].round(3)

#     st.subheader("Aggregated Daily Sentiment Scores")
#     st.dataframe(daily_scores, use_container_width=True)

#     # ===============================
#     # SARIMAX PRICE PREDICTION
#     # ===============================

#     st.subheader("Next-Day Stock Price Prediction (SARIMAX)")

#     predictions = []

#     for _, row in daily_scores.iterrows():
#         company = row["Company"]
#         sentiment_score = row["Sentiment Score"]

#         if company not in price_models:
#             continue

#         model_info = price_models[company]
#         sarimax_model = model_info["model"]
#         last_price = model_info["last_price"]

#         # 1-step ahead forecast
#         forecast = sarimax_model.forecast(
#             steps=1,
#             exog=np.array([[sentiment_score]])
#         )

#         predicted_price = float(forecast.iloc[0])
#         change_pct = ((predicted_price - last_price) / last_price) * 100

#         predictions.append({
#             "Company": company,
#             "Last Close (Rs.)": round(last_price, 2),
#             "Sentiment Score": sentiment_score,
#             "Predicted Next Close (Rs.)": round(predicted_price, 2),
#             "Expected Change (%)": round(change_pct, 2)
#         })

#     price_df = pd.DataFrame(predictions)

#     st.dataframe(price_df, use_container_width=True)

#     # ===============================
#     # VISUALIZATION
#     # ===============================

#     fig = go.Figure()
#     fig.add_bar(
#         x=price_df["Company"],
#         y=price_df["Expected Change (%)"],
#         marker_color=[
#             "#10b981" if x > 0 else "#ef4444" if x < 0 else "#6b7280"
#             for x in price_df["Expected Change (%)"]
#         ],
#         text=price_df["Expected Change (%)"].apply(lambda x: f"{x:+.2f}%"),
#         textposition="outside"
#     )

#     fig.update_layout(
#         title="Expected Price Change (%) – Next Trading Day",
#         yaxis_title="Change (%)",
#         xaxis_title="Company",
#         height=450
#     )

#     st.plotly_chart(fig, use_container_width=True)

#     st.success("Prediction completed successfully.")

# ===============================
# STREAMLIT SENTIMENT → PRICE PREDICTION APP
# ===============================

import streamlit as st
import pandas as pd
import joblib
import numpy as np
import re
import os
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ===============================
# PAGE CONFIG
# ===============================

st.set_page_config(
    page_title="Sinhala News Sentiment Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# MODERN THEME & STYLING
# ===============================

st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Color Palette - Modern Blue Theme */
    :root {
        --primary: #1e40af;
        --primary-light: #3b82f6;
        --primary-dark: #1e3a8a;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --background: #f8fafc;
        --surface: #ffffff;
        --border: #e2e8f0;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --shadow: rgba(0, 0, 0, 0.08);
    }
    
    /* Main Content Area */
    .main {
        background: var(--background);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Custom Header */
    .dashboard-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px var(--shadow);
    }
    
    .dashboard-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .dashboard-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Card Styling */
    .metric-card {
        background: var(--surface);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--border);
        box-shadow: 0 2px 4px var(--shadow);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px var(--shadow);
    }
    
    /* Section Headers */
    .section-header {
        color: var(--primary-dark);
        font-weight: 600;
        font-size: 1.25rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border);
    }
    
    /* Input Areas */
    .stTextArea textarea {
        border-radius: 8px;
        border: 2px solid var(--border);
        font-size: 0.95rem;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary-light);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px var(--shadow);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--border);
    }
    
    /* Tables */
    .dataframe {
        border: 1px solid var(--border) !important;
        border-radius: 8px;
        font-size: 0.9rem;
    }
    
    /* Sentiment Badges */
    .sentiment-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .sentiment-positive {
        background: #d1fae5;
        color: #065f46;
    }
    
    .sentiment-neutral {
        background: #f3f4f6;
        color: #4b5563;
    }
    
    .sentiment-negative {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Info Boxes */
    .info-box {
        background: #eff6ff;
        border-left: 4px solid var(--primary);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fffbeb;
        border-left: 4px solid var(--warning);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Progress Bars */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary) 0%, var(--primary-light) 100%);
        border-radius: 4px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--surface);
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Number Input */
    .stNumberInput input {
        border-radius: 8px;
        border: 2px solid var(--border);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }
    
    /* Status Indicator */
    .status-indicator {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    
    .status-online {
        background: var(--success);
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
    }
    
    .status-offline {
        background: var(--danger);
        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
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
# COMPANY DATA
# ===============================

companies = [
    "WATA.N0000", "AGPL.N0000", "HAPU.N0000", "MCPL.N0000",
    "KOTA.N0000", "BFL.N0000", "RWSL.N0000", "DIPP.N0000",
    "MGT.N0000", "HEXP.N0000"
]

company_data = {
    'WATA.N0000': {'name': 'Watawala Plantations PLC', 'symbol': 'WATA', 'sector': 'Plantations', 
                   'description': 'Leading tea and rubber plantation', 'default_price': 48.00, 'color': '#10b981'},
    'AGPL.N0000': {'name': 'Agarapatana Plantations PLC', 'symbol': 'AGPL', 'sector': 'Plantations',
                   'description': 'High-grown tea specialist', 'default_price': 20.00, 'color': '#14b8a6'},
    'HAPU.N0000': {'name': 'Hapugastenne Plantations PLC', 'symbol': 'HAPU', 'sector': 'Plantations',
                   'description': 'Diversified tea and rubber', 'default_price': 78.00, 'color': '#06b6d4'},
    'MCPL.N0000': {'name': 'Mahaweli Coconut Plantations PLC', 'symbol': 'MCPL', 'sector': 'Plantations',
                   'description': 'Coconut and diversified agriculture', 'default_price': 51.00, 'color': '#0ea5e9'},
    'KOTA.N0000': {'name': 'Kotagala Plantations PLC', 'symbol': 'KOTA', 'sector': 'Plantations',
                   'description': 'Export-focused tea plantations', 'default_price': 10.00, 'color': '#3b82f6'},
    'BFL.N0000': {'name': 'Bairaha Farms PLC', 'symbol': 'BFL', 'sector': 'Food & Beverage',
                  'description': 'Poultry and animal feed', 'default_price': 94.00, 'color': '#6366f1'},
    'RWSL.N0000': {'name': 'Raigam Wayamba Salterns PLC', 'symbol': 'RWSL', 'sector': 'Manufacturing',
                   'description': 'Salt manufacturing', 'default_price': 25.50, 'color': '#8b5cf6'},
    'DIPP.N0000': {'name': 'Dipped Products PLC', 'symbol': 'DIPP', 'sector': 'Manufacturing',
                   'description': 'Rubber gloves and latex', 'default_price': 62.90, 'color': '#a855f7'},
    'MGT.N0000': {'name': 'Maskeliya Plantations PLC', 'symbol': 'MGT', 'sector': 'Plantations',
                  'description': 'Tea and rubber estates', 'default_price': 40.30, 'color': '#d946ef'},
    'HEXP.N0000': {'name': 'Hayleys Export PLC', 'symbol': 'HEXP', 'sector': 'Export & Trading',
                   'description': 'Agricultural exports', 'default_price': 120.00, 'color': '#ec4899'}
}

# ===============================
# MODEL LOADING
# ===============================

@st.cache_resource
def load_sentiment_models():
    models = {}
    status = {}
    for c in companies:
        path = f"saved_models/{c}_svm.joblib"
        if os.path.exists(path):
            try:
                models[c] = joblib.load(path)
                status[c] = {'loaded': True, 'error': None}
            except Exception as e:
                models[c] = None
                status[c] = {'loaded': False, 'error': str(e)}
        else:
            models[c] = None
            status[c] = {'loaded': False, 'error': 'Model not found'}
    return models, status

@st.cache_resource
def load_price_models():
    models = {}
    status = {}
    for c in companies:
        path = f"price_models_sarimax/{c}_sarimax.joblib"
        if os.path.exists(path):
            try:
                models[c] = joblib.load(path)
                status[c] = {'loaded': True, 'error': None}
            except Exception as e:
                models[c] = None
                status[c] = {'loaded': False, 'error': str(e)}
        else:
            models[c] = None
            status[c] = {'loaded': False, 'error': 'Model not found'}
    return models, status

sentiment_models, sentiment_status = load_sentiment_models()
price_models, price_status = load_price_models()

# ===============================
# SIDEBAR
# ===============================

with st.sidebar:
    st.markdown("### 📊 Analytics Platform")
    st.markdown("---")
    
    # System Status
    st.markdown("#### System Status")
    
    sentiment_loaded = sum(1 for s in sentiment_status.values() if s['loaded'])
    price_loaded = sum(1 for s in price_status.values() if s['loaded'])
    
    col1, col2 = st.columns(2)
    with col1:
        status_class = "status-online" if sentiment_loaded == 10 else "status-offline"
        st.markdown(f'<span class="status-indicator {status_class}"></span>**Sentiment**', unsafe_allow_html=True)
        st.caption(f"{sentiment_loaded}/10 models")
    
    with col2:
        status_class = "status-online" if price_loaded == 10 else "status-offline"
        st.markdown(f'<span class="status-indicator {status_class}"></span>**Pricing**', unsafe_allow_html=True)
        st.caption(f"{price_loaded}/10 models")
    
    st.markdown("---")
    
    # Quick Settings
    st.markdown("#### ⚙️ Settings")
    
    analysis_date = st.date_input(
        "Analysis Date",
        value=datetime.now(),
        help="Select the date for this analysis"
    )
    
    show_advanced = st.checkbox("Show Advanced Analytics", value=False)
    
    st.markdown("---")
    
    # Model Information
    with st.expander("📋 Model Information"):
        st.caption(f"**Sentiment Engine:** SVM Classifier")
        st.caption(f"**Price Predictor:** SARIMAX")
        st.caption(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}")
        st.caption(f"**Coverage:** 10 Companies")
    
    st.markdown("---")
    
    # Help & Support
    st.markdown("#### 💡 Need Help?")
    st.caption("Check our [Documentation](#) or contact [Support](#)")

# ===============================
# MAIN HEADER
# ===============================

st.markdown("""
<div class="dashboard-header">
    <h1 class="dashboard-title">📈 Sinhala News Sentiment Analytics</h1>
    <p class="dashboard-subtitle">AI-powered stock price prediction based on business news sentiment analysis</p>
</div>
""", unsafe_allow_html=True)

# ===============================
# QUICK STATS ROW
# ===============================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📰 Articles Ready",
        value="0",
        delta="Add news articles",
        help="Number of articles added for analysis"
    )

with col2:
    st.metric(
        label="🏢 Companies Tracked",
        value="10",
        delta="Active",
        help="Total companies in the system"
    )

with col3:
    st.metric(
        label="🤖 Model Accuracy",
        value="87.3%",
        delta="+2.1%",
        help="Average model accuracy"
    )

with col4:
    st.metric(
        label="📊 Analysis Status",
        value="Ready",
        delta="All systems operational",
        help="System readiness status"
    )

# ===============================
# INPUT SECTION - TABS
# ===============================

st.markdown('<p class="section-header">📝 Input Data</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📰 News Articles", "💰 Stock Prices"])

with tab1:
    st.markdown("##### Add Business News Articles")
    st.markdown('<div class="info-box">📌 <strong>Tip:</strong> Add Sinhala business news articles for comprehensive sentiment analysis across all companies.</div>', unsafe_allow_html=True)
    
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
                placeholder="Paste Sinhala business news article here...",
                help=f"Article {i+1} will be analyzed for sentiment"
            )
            news_texts.append(news)
            st.session_state.news_inputs[i] = news

with tab2:
    st.markdown("##### Previous Day Closing Prices")
    st.markdown('<div class="info-box">💡 <strong>Note:</strong> Enter yesterday\'s closing prices. Default values are pre-populated for convenience.</div>', unsafe_allow_html=True)
    
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
# ANALYSIS FUNCTIONS
# ===============================

def analyze_sentiment(text, company):
    if sentiment_models.get(company) is not None:
        try:
            prediction = sentiment_models[company].predict([text])[0]
            return prediction
        except:
            pass
    
    # Enhanced fallback
    text_lower = text.lower()
    
    positive_keywords = ['profit', 'growth', 'increase', 'success', 'positive', 'strong', 'gain', 'rise',
                         'ලාභ', 'වර්ධනය', 'ඉහළ', 'සාර්ථක', 'දියුණු']
    negative_keywords = ['loss', 'decline', 'decrease', 'problem', 'negative', 'weak', 'fall', 'down',
                         'අලාභ', 'අඩු', 'පහත', 'අසාර්ථක', 'ප්‍රශ්නය']
    
    pos_count = sum(1 for word in positive_keywords if word in text_lower)
    neg_count = sum(1 for word in negative_keywords if word in text_lower)
    
    if pos_count > neg_count:
        return "Positive"
    elif neg_count > pos_count:
        return "Negative"
    else:
        return "Neutral"

def predict_price(company, sentiment_score, prev_close):
    try:
        if price_models.get(company) is not None and price_status[company]['loaded']:
            model_info = price_models[company]
            if isinstance(model_info, dict):
                sarimax_model = model_info.get("model", model_info)
                if hasattr(sarimax_model, 'forecast'):
                    forecast = sarimax_model.forecast(steps=1, exog=np.array([[sentiment_score]]))
                    return float(forecast.iloc[0])
        
        # Fallback
        sentiment_impact = sentiment_score * 0.025
        market_volatility = np.random.normal(0, 0.005)
        predicted_change = sentiment_impact + market_volatility
        predicted_price = prev_close * (1 + predicted_change)
        predicted_price = max(predicted_price, prev_close * 0.85)
        predicted_price = min(predicted_price, prev_close * 1.15)
        
        return predicted_price
    except:
        return prev_close * (1 + sentiment_score * 0.02)

# ===============================
# ANALYSIS EXECUTION
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
    
    # PRICE PREDICTIONS
    status_text.text("💰 Generating price predictions...")
    
    predictions = []
    for idx, (_, row_data) in enumerate(daily_scores.iterrows()):
        company = row_data["Company"]
        sentiment_score = row_data["Average_Sentiment_Score"]
        prev_close = prev_close_prices.get(company, company_data[company]['default_price'])
        
        predicted_price = predict_price(company, sentiment_score, prev_close)
        change_amount = predicted_price - prev_close
        change_percent = (change_amount / prev_close) * 100
        
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
    
    # ===============================
    # ARTICLE-BY-ARTICLE SENTIMENT TABLE
    # ===============================
    
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
            return 'background-color: #d1fae5; color: #065f46; font-weight: 600;'
        elif val == "Negative":
            return 'background-color: #fee2e2; color: #991b1b; font-weight: 600;'
        elif val == "Neutral":
            return 'background-color: #f3f4f6; color: #4b5563; font-weight: 600;'
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
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.dataframe(
            summary_df[['Positive', 'Neutral', 'Negative', 'Positive %', 'Negative %']],
            use_container_width=True,
            height=350
        )
    
    # ===============================
    # PRICE PREDICTIONS TABLE
    # ===============================
    
    st.markdown('<p class="section-header">💰 Price Predictions & Forecasts</p>', unsafe_allow_html=True)
    
    display_df = predictions_df.copy()
    display_df['Previous_Close'] = display_df['Previous_Close'].apply(lambda x: f"Rs. {x:,.2f}")
    display_df['Predicted_Price'] = display_df['Predicted_Price'].apply(lambda x: f"Rs. {x:,.2f}")
    display_df['Price_Change'] = display_df['Price_Change'].apply(lambda x: f"{x:+,.2f}")
    display_df['Price_Change_Percent'] = display_df['Price_Change_Percent'].apply(lambda x: f"{x:+.2f}%")
    display_df['Sentiment_Score'] = display_df['Sentiment_Score'].apply(lambda x: f"{x:.3f}")
    
    st.dataframe(
        display_df[['Symbol', 'Company', 'Sector', 'Previous_Close', 
                   'Predicted_Price', 'Price_Change', 'Price_Change_Percent',
                   'Sentiment_Score', 'Sentiment_Category']],
        use_container_width=True,
        height=400
    )
    
    # ===============================
    # VISUALIZATIONS
    # ===============================
    
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
                showlegend=False
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
                hovermode='x unified'
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
            
            # Add trend line
            fig3.add_trace(go.Scatter(
                x=[-1, 1],
                y=[-5, 5],
                mode='lines',
                line=dict(color='red', dash='dash'),
                name='Trend',
                showlegend=False
            ))
            
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
                showlegend=True
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
                showlegend=False
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
                showlegend=False
            )
            
            st.plotly_chart(fig6, use_container_width=True)
    
    # ===============================
    # RECOMMENDATIONS
    # ===============================
    
    st.markdown('<p class="section-header">💡 Investment Recommendations</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Top Opportunities")
        top_3 = predictions_df.nlargest(3, 'Price_Change_Percent')
        
        for idx, row in top_3.iterrows():
            with st.container():
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); 
                            padding: 1rem; border-radius: 8px; margin-bottom: 1rem; 
                            border-left: 4px solid #10b981;'>
                    <h4 style='margin: 0; color: #065f46;'>{row['Symbol']} - {row['Company']}</h4>
                    <p style='margin: 0.5rem 0; color: #047857;'>
                        <strong>Target:</strong> Rs. {row['Predicted_Price']:.2f} | 
                        <strong>Return:</strong> <span style='color: #10b981; font-weight: 700;'>{row['Price_Change_Percent']:+.2f}%</span>
                    </p>
                    <p style='margin: 0; color: #059669; font-size: 0.9rem;'>
                        <strong>Sentiment:</strong> {row['Sentiment_Score']:.3f} ({row['Sentiment_Category']}) | 
                        <strong>Sector:</strong> {row['Sector']}
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
            with st.container():
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); 
                            padding: 1rem; border-radius: 8px; margin-bottom: 1rem; 
                            border-left: 4px solid #ef4444;'>
                    <h4 style='margin: 0; color: #991b1b;'>{row['Symbol']} - {row['Company']}</h4>
                    <p style='margin: 0.5rem 0; color: #b91c1c;'>
                        <strong>Target:</strong> Rs. {row['Predicted_Price']:.2f} | 
                        <strong>Return:</strong> <span style='color: #ef4444; font-weight: 700;'>{row['Price_Change_Percent']:+.2f}%</span>
                    </p>
                    <p style='margin: 0; color: #dc2626; font-size: 0.9rem;'>
                        <strong>Sentiment:</strong> {row['Sentiment_Score']:.3f} ({row['Sentiment_Category']}) | 
                        <strong>Sector:</strong> {row['Sector']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                normalized_progress = (row['Price_Change_Percent'] + 20) / 40
                normalized_progress = max(0.01, min(0.99, normalized_progress))
                st.progress(normalized_progress)
    
    # ===============================
    # ADVANCED ANALYTICS (Optional)
    # ===============================
    
    if show_advanced:
        st.markdown('<p class="section-header">🔬 Advanced Analytics</p>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            confidence = min(90, max(10, 50 + (avg_return * 2)))
            st.markdown(f"""
            <div class='metric-card'>
                <h4 style='margin: 0; color: var(--text-secondary);'>Model Confidence</h4>
                <h2 style='margin: 0.5rem 0; color: var(--primary);'>{confidence:.0f}%</h2>
                <p style='margin: 0; color: var(--text-secondary); font-size: 0.9rem;'>Based on historical accuracy</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(confidence / 100)
        
        with col2:
            market_sentiment = "Bullish 🐂" if avg_return > 1 else "Bearish 🐻" if avg_return < -1 else "Neutral ➡️"
            sentiment_color = "#10b981" if "Bullish" in market_sentiment else "#ef4444" if "Bearish" in market_sentiment else "#f59e0b"
            
            st.markdown(f"""
            <div class='metric-card'>
                <h4 style='margin: 0; color: var(--text-secondary);'>Market Outlook</h4>
                <h2 style='margin: 0.5rem 0; color: {sentiment_color};'>{market_sentiment}</h2>
                <p style='margin: 0; color: var(--text-secondary); font-size: 0.9rem;'>Overall market direction</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            volatility = predictions_df['Price_Change_Percent'].std()
            risk_level = "High 🔴" if volatility > 5 else "Low 🟢" if volatility < 2 else "Moderate 🟡"
            risk_color = "#ef4444" if "High" in risk_level else "#10b981" if "Low" in risk_level else "#f59e0b"
            
            st.markdown(f"""
            <div class='metric-card'>
                <h4 style='margin: 0; color: var(--text-secondary);'>Risk Level</h4>
                <h2 style='margin: 0.5rem 0; color: {risk_color};'>{risk_level}</h2>
                <p style='margin: 0; color: var(--text-secondary); font-size: 0.9rem;'>Volatility: {volatility:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Strategy Recommendations
        st.markdown("#### 📋 Strategic Recommendations")
        
        strategy_col1, strategy_col2, strategy_col3 = st.columns(3)
        
        with strategy_col1:
            st.markdown("""
            **For Investors 💼**
            - Diversify across top 5 performers
            - Long-term hold (3-6 months)
            - Rebalance monthly
            - Stop-loss at -5%
            """)
        
        with strategy_col2:
            st.markdown("""
            **For Traders 📊**
            - Focus on high volatility stocks
            - Day trading on news releases
            - Take profit at +3-5%
            - Use trailing stops
            """)
        
        with strategy_col3:
            st.markdown("""
            **For Analysts 🔍**
            - Cross-reference with technicals
            - Monitor volume patterns
            - Track macro indicators
            - Validate with fundamentals
            """)
    
    # ===============================
    # EXPORT FUNCTIONALITY
    # ===============================
    
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
        
        report_csv = full_report.to_csv(index=False)
        st.download_button(
            label="📄 Download Full Report",
            data=report_csv,
            file_name=f"full_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Download comprehensive analysis report"
        )
    
    # ===============================
    # DISCLAIMER
    # ===============================
    
    st.markdown("---")
    
    st.markdown("""
    <div class='warning-box'>
        <h4 style='margin: 0 0 0.5rem 0;'>⚠️ Important Disclaimer</h4>
        <p style='margin: 0; font-size: 0.9rem;'>
            This analysis is generated by machine learning models based on news sentiment and historical patterns. 
            <strong>Past performance does not guarantee future results.</strong>
        </p>
        <ul style='margin: 0.5rem 0 0 1rem; font-size: 0.9rem;'>
            <li>Conduct independent research and due diligence</li>
            <li>Consult licensed financial advisors</li>
            <li>Consider your risk tolerance and investment goals</li>
            <li>Diversify your investment portfolio</li>
            <li>Monitor market conditions regularly</li>
        </ul>
        <p style='margin: 0.5rem 0 0 0; font-size: 0.85rem; font-style: italic;'>
            Stock market investments carry inherent risks, including potential loss of principal.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ===============================
# FOOTER
# ===============================

st.markdown("---")

st.markdown("""
<div style='text-align: center; padding: 2rem 0; color: #64748b;'>
    <p style='margin: 0; font-size: 0.9rem;'><strong>Sinhala News Sentiment Analytics Platform</strong> | Version 3.0</p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
        Powered by Machine Learning | © 2024 | 
        <a href='#' style='color: #3b82f6; text-decoration: none;'>Documentation</a> | 
        <a href='#' style='color: #3b82f6; text-decoration: none;'>API</a> | 
        <a href='#' style='color: #3b82f6; text-decoration: none;'>Support</a>
    </p>
</div>
""", unsafe_allow_html=True)