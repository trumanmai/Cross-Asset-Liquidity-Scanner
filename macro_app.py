import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from scipy.stats import zscore
from ta.momentum import RSIIndicator

# --- UI CONFIG ---
st.set_page_config(page_title="Institutional Macro Terminal", layout="wide")
st.markdown("<h1 style='text-align: center; color: #00f2ff;'>📊 INTRADAY LIQUIDITY & VOLATILITY SCANNER</h1>", unsafe_allow_html=True)

# --- SIDEBAR: STRATEGY PARAMETERS ---
with st.sidebar:
    st.header("⚙️ Terminal Configuration")
    ticker = st.text_input("Primary Asset", "SPY")
    bench = st.text_input("Volatility Benchmark", "^VIX")
    target_date = st.date_input("Analysis Date", value=pd.to_datetime("2026-04-22"))
    sensitivity = st.slider("Outlier Sensitivity (Z-Score)", 1.0, 5.0, 2.5)
    rsi_period = st.slider("RSI Lookback Period", 5, 30, 14)

# --- DATA & QUANT ENGINE ---
@st.cache_data
def get_ultra_data(t1, t2, d):
    start_str = d.strftime('%Y-%m-%d')
    end_str = (d + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    df = yf.download([t1, t2], start=start_str, end=end_str, interval="1m")['Close']
    if df.empty: return None
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return df.dropna()

data = get_ultra_data(ticker, bench, target_date)

if data is not None:
    # 1. Math: Normalization & Z-Scores
    norm_df = ((data / data.iloc[0]) - 1) * 100
    returns = data[ticker].pct_change().fillna(0)
    data['Z_Score'] = zscore(returns)
    
    # 2. Math: RSI Momentum (Python 3.14 compatible via 'ta' library)
    rsi_io = RSIIndicator(close=data[ticker], window=rsi_period)
    data['RSI'] = rsi_io.rsi()
    
    # 3. Math: Lead-Lag Analysis
    lag_corr = data[bench].shift(5).corr(data[ticker])
    shocks = data[(data['Z_Score'].abs() > sensitivity)]

    # --- VISUALIZATION ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, row_heights=[0.7, 0.3],
                        specs=[[{"secondary_y": True}], [{"secondary_y": False}]])

    # Row 1: Price & Volatility
    fig.add_trace(go.Scatter(x=norm_df.index, y=norm_df[ticker], name=f"{ticker} Return", 
                             line=dict(color='#00f2ff', width=2)), row=1, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(x=norm_df.index, y=norm_df[bench], name="Benchmark Volatility", 
                             line=dict(color='orange', width=1, dash='dot')), row=1, col=1, secondary_y=True)
    fig.add_trace(go.Scatter(x=shocks.index, y=norm_df.loc[shocks.index, ticker],
                             mode='markers', name="QUANT SIGNAL",
                             marker=dict(color='red', size=10, symbol='x')), row=1, col=1, secondary_y=False)

    # Row 2: RSI Momentum
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name="Relative Strength Index", 
                             line=dict(color='magenta', width=1.5)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    # --- FINAL TOUCHES: MARGINS & WATERMARK ---
    fig.update_layout(
        template="plotly_dark", 
        height=800, 
        hovermode="x unified",
        paper_bgcolor="#000", 
        plot_bgcolor="#000", 
        showlegend=True,
        margin=dict(l=20, r=20, t=50, b=40),
        annotations=[dict(
            text="Developed by Truman Mai",
            xref="paper", yref="paper",
            x=1, y=-0.08,
            showarrow=False,
            font=dict(size=12, color="gray")
        )]
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # --- ANALYTICS DASHBOARD ---
    st.markdown("### 📈 Analytical Diagnostics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Asset-Bench Correlation", f"{lag_corr:.2f}")
    c2.metric("RSI Level", f"{data['RSI'].iloc[-1]:.1f}" if not pd.isna(data['RSI'].iloc[-1]) else "N/A")
    c3.metric("Outlier Signals", len(shocks))
    
    # Backtest Logic: Mean return 10 minutes after a shock
    if len(shocks) > 0:
        future_returns = []
        for idx in shocks.index:
            try:
                curr_loc = data.index.get_loc(idx)
                if curr_loc + 10 < len(data):
                    future_price = data.iloc[curr_loc + 10][ticker]
                    current_price = data.iloc[curr_loc][ticker]
                    future_returns.append((future_price / current_price) - 1)
            except: continue
        avg_win = np.mean(future_returns) * 100 if future_returns else 0
        c4.metric("Mean 10m Post-Signal Return", f"{avg_win:.3f}%")

else:
    st.error("Data Retrieval Error: Connection to exchange API failed or data not available for this date.")