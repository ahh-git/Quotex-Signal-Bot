# main.py
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import time
from datetime import datetime
import config
from indicators import TechnicalAnalyzer
from auth_handler import AuthManager

# --- 1. SETUP & STYLES ---
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS Injection
st.markdown("""
    <style>
        /* General Theme */
        .stApp { background-color: #0b141a; }
        
        /* Card Styling */
        .metric-container {
            background-color: #15202b;
            border: 1px solid #253341;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        /* Signal Badges */
        .signal-call {
            background-color: #00E396;
            color: #000;
            padding: 15px;
            border-radius: 8px;
            font-size: 28px;
            font-weight: 900;
            text-align: center;
            box-shadow: 0 0 20px rgba(0, 227, 150, 0.4);
            animation: pulse 2s infinite;
        }
        .signal-put {
            background-color: #FF4560;
            color: #fff;
            padding: 15px;
            border-radius: 8px;
            font-size: 28px;
            font-weight: 900;
            text-align: center;
            box-shadow: 0 0 20px rgba(255, 69, 96, 0.4);
            animation: pulse 2s infinite;
        }
        .signal-wait {
            background-color: #FEB019;
            color: #000;
            padding: 15px;
            border-radius: 8px;
            font-size: 28px;
            font-weight: 900;
            text-align: center;
            opacity: 0.7;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }

        /* Profile Section */
        .profile-box {
            display: flex;
            align-items: center;
            padding: 10px;
            background: #1e2a36;
            border-radius: 50px;
            margin-bottom: 20px;
        }
        .profile-pic {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 10px;
        }
    </style>
""", unsafe_allow_html=True)

auth = AuthManager()

# --- 2. LOGIN VIEW ---
if not auth.is_authenticated():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"<h1 style='text-align: center; color: #00E396;'>{config.APP_NAME}</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #888;'>Professional Trading Intelligence</h3>", unsafe_allow_html=True)
        st.write("---")
        st.warning("⚠️ DISCLAIMER: This tool is for educational analysis only. Trading involves risk.")
        
        st.markdown("### Authentication Required")
        if st.button("🔵 Sign in with Google (One Tap)", use_container_width=True):
            auth.login_google_mock()
    st.stop()

# --- 3. MAIN DASHBOARD ---
user = auth.get_user()

# Sidebar
with st.sidebar:
    # User Profile Widget
    st.markdown(f"""
        <div class="profile-box">
            <img src="{user['photo']}" class="profile-pic">
            <div>
                <div style="font-weight: bold; font-size: 14px;">{user['name']}</div>
                <div style="font-size: 10px; color: #aaa;">PREMIUM MEMBER</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.header("Asset Configuration")
    selected_asset_label = st.selectbox("Select Asset Pair", list(config.ASSETS.keys()))
    ticker = config.ASSETS[selected_asset_label]
    
    timeframe = st.radio("Signal Timeframe", ["1 Minute (Turbo)", "5 Minutes (Intraday)"])
    tf_code = "1m" if "1 Minute" in timeframe else "5m"
    
    st.markdown("---")
    if st.button("🔴 Logout"):
        auth.logout()

# Main Area
st.title(f"{selected_asset_label} Analysis")

# DATA LOADING WITH ANIMATION
with st.status("Initializing Neural Engine...", expanded=True) as status:
    st.write("Fetching live market feeds...")
    # Fetch Data
    try:
        data = yf.download(ticker, period="1d", interval=tf_code, progress=False)
        # Drop multi-index if exists (common yfinance issue in 2024/2025)
        if hasattr(data.columns, 'droplevel'):
             data.columns = data.columns.droplevel(1) if data.columns.nlevels > 1 else data.columns
             
        st.write("Calculating Bollinger Bands & RSI...")
        analyzer = TechnicalAnalyzer(data)
        processed_data = analyzer.calculate_all()
        
        st.write("Running Logic Matrix...")
        current_candle = processed_data.iloc[-1]
        analysis = analyzer.get_signal_strength(current_candle)
        
        status.update(label="Analysis Complete", state="complete", expanded=False)
    except Exception as e:
        st.error(f"Data Feed Error: {e}")
        st.stop()

# --- 4. SIGNAL DISPLAY ---
col_sig, col_conf, col_detail = st.columns([2, 1, 2])

with col_sig:
    st.markdown("### Generated Signal")
    sig_text = analysis['signal']
    if "CALL" in sig_text:
        st.markdown(f'<div class="signal-call">{sig_text}</div>', unsafe_allow_html=True)
    elif "PUT" in sig_text:
        st.markdown(f'<div class="signal-put">{sig_text}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="signal-wait">{sig_text}</div>', unsafe_allow_html=True)

with col_conf:
    st.markdown("### Accuracy")
    st.markdown(f"""
        <div class="metric-container">
            <h1 style="color: #00E396; margin: 0;">{int(analysis['confidence'])}%</h1>
            <small>AI Confidence</small>
        </div>
    """, unsafe_allow_html=True)

with col_detail:
    st.markdown("### Technical Reasons")
    if analysis['reasons']:
        for r in analysis['reasons']:
            st.markdown(f"✅ *{r}*")
    else:
        st.info("Market is ranging. No clear bias detected.")

# --- 5. LIVE CHART ---
st.subheader("Live Market Preview")

fig = go.Figure()

# Candlesticks
fig.add_trace(go.Candlestick(
    x=processed_data.index,
    open=processed_data['Open'],
    high=processed_data['High'],
    low=processed_data['Low'],
    close=processed_data['Close'],
    name="Price"
))

# Bollinger Bands (Updated names)
fig.add_trace(go.Scatter(
    x=processed_data.index, 
    y=processed_data['UpperBB'], # Changed from BBU_20_2.0
    line=dict(color='gray', width=1, dash='dot'), 
    name='Upper Band'
))

fig.add_trace(go.Scatter(
    x=processed_data.index, 
    y=processed_data['LowerBB'], # Changed from BBL_20_2.0
    line=dict(color='gray', width=1, dash='dot'), 
    name='Lower Band'
))

st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown(f"<div style='text-align:center; color: #555; margin-top: 50px;'>Quotex Signal Bot {config.VERSION} | Execute trades at your own risk.</div>", unsafe_allow_html=True)
