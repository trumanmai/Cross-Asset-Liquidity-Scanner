# Cross-Asset-Liquidity-Scanner
Intraday Cross-Asset Liquidity Scanner. Quant terminal built in Python to detect institutional liquidity shocks via Z-score outlier detection. Features dual-axis volatility correlation (^VIX), RSI momentum filtering, and automated 10m post-signal alpha backtesting. Built by Truman Mai.
# Intraday Cross-Asset Liquidity Scanner

A quantitative analysis terminal designed to identify institutional liquidity shocks and market anomalies in real-time.

## Key Features
* **Outlier Detection**: Uses Z-score logic to identify statistical price shocks.
* **Momentum Filtering**: Integrated RSI (Relative Strength Index) to validate signal strength.
* **Lead-Lag Analysis**: Quantifies the correlation between asset price action and benchmark volatility (^VIX).
* **Backtesting**: Automated 10-minute post-signal alpha calculation to evaluate strategy performance.

## Tech Stack
* **Language**: Python 3.14
* **Libraries**: Streamlit, Plotly, YFinance, Scipy, TA-Lib
* **Deployment**: Streamlit Community Cloud

**Developed by Truman Mai**
