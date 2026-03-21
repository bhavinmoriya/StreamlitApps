import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# --- App Title ---
st.title("📉 Covariance & Correlation Checker for Securities")
st.markdown("""
Check how your favorite stocks move together using **covariance** and **correlation**.
*Powered by YFinance + Streamlit*
""")

# --- Sidebar: User Inputs ---
st.sidebar.header("Settings")
tickers = st.sidebar.text_input(
    "Enter Tickers (comma-separated, e.g., AAPL,MSFT,GOOGL)",
    "AAPL,MSFT,GOOGL,AMZN,JPM"
)
tickers = [t.strip().upper() for t in tickers.split(",")]

period = st.sidebar.selectbox(
    "Time Period",
    ["1y", "2y", "5y", "10y", "YTD", "Max"],
    index=0
)

# --- Fetch Data ---
@st.cache_data  # Cache to avoid repeated downloads
def fetch_data(tickers, period):
    st.sidebar.write(f"🔄 Fetching data for {len(tickers)} securities...")
    data = yf.download(tickers, period=period)["Close"]
    return data.dropna()

try:
    data = fetch_data(tickers, period)
    returns = data.pct_change().dropna()

    # --- Calculate Metrics ---
    cov_matrix = returns.cov() * 252  # Annualized covariance
    corr_matrix = returns.corr()      # Correlation

    # --- Display Raw Data ---
    st.subheader("📊 Price Data")
    st.dataframe(data.tail())

    # --- Covariance Matrix ---
    st.subheader("📈 Annualized Covariance Matrix")
    st.dataframe(cov_matrix.style.background_gradient(cmap="viridis"))

    # --- Correlation Matrix + Heatmap ---
    st.subheader("🔗 Correlation Matrix")
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(corr_matrix.style.background_gradient(cmap="coolwarm"))
    with col2:
        fig, ax = plt.subplots()
        sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    # --- Pairplot (Scatter Matrix) ---
    st.subheader("📉 Pairwise Relationships")
    fig = sns.pairplot(pd.DataFrame(returns, columns=tickers))
    st.pyplot(fig)

    # --- Key Insights ---
    st.subheader("💡 Key Insights")
    max_corr = corr_matrix.abs().max().max()
    min_corr = corr_matrix.abs().min().min()
    st.write(f"- **Highest absolute correlation**: {max_corr:.2f} (between {corr_matrix.abs().stack().idxmax()})")
    st.write(f"- **Lowest absolute correlation**: {min_corr:.2f} (between {corr_matrix.abs().stack().idxmin()})")

    # --- Download Button ---
    st.download_button(
        label="📥 Download Covariance Matrix (CSV)",
        data=cov_matrix.to_csv().encode("utf-8"),
        file_name="covariance_matrix.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"❌ Error: {e}. Check tickers and try again!")

# --- Footer ---
st.markdown("---")
st.markdown("""
*Data Source: [Yahoo Finance](https://finance.yahoo.com) | App by Bhavin K. Moriya*
""")
