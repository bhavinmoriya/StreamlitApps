import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
plt.style.use("ggplot")
from datetime import date, timedelta


@st.cache_data(show_spinner=False)
def load_returns(ticker: str, years: int) -> pd.Series:
    """Download daily close prices and compute daily returns."""
    end = date.today()
    start = end - timedelta(days=int(years * 365.25))
    data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if data.empty:
        return pd.Series(dtype=float)
    close = data["Close"]
    if isinstance(close, pd.DataFrame):  # yfinance may return a one-column DataFrame
        close = close.squeeze()
    return close.pct_change().dropna()


def calculate_var_cvar(returns, confidence_level=0.95):
    """
    Calculate historical Value at Risk (VaR) and
    Conditional Value at Risk (CVaR / Expected Shortfall).

    Returns a dict with VaR and CVaR as positive loss percentages.
    """
    returns = np.asarray(returns).flatten()
    returns = returns[~np.isnan(returns)]

    alpha = 1 - confidence_level

    # VaR: the alpha-quantile of the loss distribution
    var = np.percentile(returns, 100 * alpha)

    # CVaR / ES: average loss beyond the VaR threshold
    tail_losses = returns[returns <= var]
    cvar = tail_losses.mean()

    return {
        "confidence_level": confidence_level,
        "VaR": -var,
        "CVaR": -cvar,
        "number_of_tail_observations": len(tail_losses),
    }


# ---------------- UI ----------------

st.set_page_config(page_title="VaR / CVaR Explorer", layout="wide")
st.title("📉 VaR / CVaR Explorer")
st.caption("Historical VaR & CVaR with tail-risk thresholds on the daily returns histogram.")

col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input("Ticker", value="AAPL").strip().upper()
with col2:
    years = st.select_slider("Period (years)", options=[5, 6, 7, 8, 9, 10], value=10)
with col3:
    confidence = st.select_slider("Confidence level", options=[90, 95, 99], value=95)

run = st.button("Run", type="primary")

if run or ("_has_run" in st.session_state):
    st.session_state["_has_run"] = True

    with st.spinner(f"Downloading {ticker} data..."):
        returns = load_returns(ticker, years)

    if returns.empty:
        st.error(f"No data found for ticker '{ticker}'. Check the symbol and try again.")
        st.stop()

    results = calculate_var_cvar(returns, confidence_level=confidence / 100)

    # --- Metrics ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"Daily VaR ({confidence:.0f}%)", f"{results['VaR']:.2%}")
    m2.metric(f"Daily CVaR ({confidence:.0f}%)", f"{results['CVaR']:.2%}")
    m3.metric("Tail observations", f"{results['number_of_tail_observations']}")
    m4.metric("Observations", f"{len(returns)}")

    st.info(
        f"**{ticker}** over the last **{years} years**: on {(100 - confidence):.0f}% of days, "
        f"the daily loss exceeded **{results['VaR']:.2%}** (VaR); "
        f"when it did, the average loss was **{results['CVaR']:.2%}** (CVaR)."
    )

    # --- Histogram with VaR / CVaR thresholds ---
    flat_returns = returns.values.flatten()
    flat_returns = flat_returns[~np.isnan(flat_returns)]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(flat_returns, bins=100, color="steelblue", edgecolor="white", alpha=0.8)

    var_x = -results["VaR"]
    cvar_x = -results["CVaR"]

    ax.axvline(var_x, color="red", linestyle="--", linewidth=2,
               label=f"VaR ({confidence:.0f}%): {results['VaR']:.2%}")
    ax.axvline(cvar_x, color="darkorange", linestyle="-.", linewidth=2,
               label=f"CVaR ({confidence:.0f}%): {results['CVaR']:.2%}")

    # Shade the tail beyond VaR
    tail = flat_returns[flat_returns <= var_x]
    if len(tail):
        ax.hist(tail, bins=30, color="tomato", alpha=0.6)

    ax.set_title(f"Distribution of Daily Returns for {ticker} (with Tail Risk Thresholds)")
    ax.set_xlabel("Daily Return")
    ax.set_ylabel("Frequency")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)
else:
    st.markdown(
        """
        **How to run locally:**
        ```bash
        pip install streamlit yfinance pandas numpy matplotlib
        streamlit run app.py
        ```
        Pick a **ticker**, a **period** (5–10 years), and a **confidence level** (90 / 95 / 99%),
        then hit **Run** to see the returns histogram with VaR and CVaR thresholds.
        """
    )
