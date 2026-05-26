import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Page config - keeping it clean and professional
st.set_page_config(page_title="Michael's Market Dashboard", layout="wide")
st.title("📊 Michael's Market Dashboard")
st.caption("Built by Michael | Data via Yahoo Finance | Still learning, always improving")

# --- Sidebar ---
st.sidebar.header("Controls")
st.sidebar.markdown("Use the options below to explore different stocks and time ranges.")

# Stock groups - a mix of things I'm studying as I learn the market
stock_groups = {
    "Tech": ["AAPL", "TSLA", "MSFT", "GOOG", "META", "NVDA", "NFLX"],
    "Banking": ["DB", "JPM", "BAC", "GS"],
    "Payments & ETFs": ["V", "MA", "AMZN", "SPY"]
}

# Quick sector selection - useful when I want to compare a whole sector at once
st.sidebar.subheader("Select by Sector")
sector_selection = []
for sector, tickers in stock_groups.items():
    if st.sidebar.checkbox(f"Select all {sector}", value=False):
        sector_selection.extend(tickers)

# Flatten all stocks into one list for the multiselect
all_symbols = [s for group in stock_groups.values() for s in group]

# Default to a few I'm currently keeping an eye on
symbols = st.sidebar.multiselect(
    "Choose stock symbols:",
    all_symbols,
    default=["AAPL", "TSLA", "SPY"] if not sector_selection else sector_selection
)

# Time range - I usually start with 6 months to get a decent trend view
period = st.sidebar.selectbox(
    "Select time range:",
    ["1mo", "3mo", "6mo", "1y", "5y"],
    index=2
)

# --- Fetch and display data ---
if symbols:
    # Pull closing prices from Yahoo Finance
    data = yf.download(symbols, period=period, interval="1d")["Close"]

    # yfinance returns a Series when only one stock is picked - this converts it to a DataFrame
    if isinstance(data, pd.Series):
        data = data.to_frame()

    # Price chart - good starting point to see overall movement
    st.subheader(f"Stock Prices Over {period}")
    st.line_chart(data)

    # Moving averages help smooth out the noise and show the bigger trend
    st.subheader("Moving Averages")
    ma_window = st.sidebar.slider("Moving Average Window (days)", 5, 50, 20)
    fig, ax = plt.subplots(figsize=(12, 5))
    for symbol in symbols:
        ax.plot(data.index, data[symbol], label=f"{symbol} Close")
        ax.plot(data.index, data[symbol].rolling(ma_window).mean(),
                linestyle="--", label=f"{symbol} {ma_window}d MA")
    ax.legend()
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    st.pyplot(fig)

    # Daily returns show how much the price moved each day (positive or negative)
    st.subheader("Daily Returns (%)")
    daily_returns = data.pct_change().dropna()
    st.line_chart(daily_returns)

    # Summary stats - mean return and volatility are two things I'm learning to interpret
    st.subheader("📑 Summary Statistics")
    summary = pd.DataFrame({
        "Mean Daily Return (%)": daily_returns.mean() * 100,
        "Volatility (%)": daily_returns.std() * 100
    })
    st.dataframe(summary.style.format("{:.2f}"))

else:
    st.warning("Pick at least one stock from the sidebar to get started.")
