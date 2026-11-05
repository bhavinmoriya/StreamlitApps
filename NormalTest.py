import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import scipy.stats as stats

st.set_page_config(page_title="Normality Testing Dashboard", layout="wide", page_icon="📊")

# ----------------------------- Helpers -----------------------------

@st.cache_data(show_spinner="Running Lilliefors Monte Carlo simulation…")
def lilliefors_null_dist(n, n_sim=2000, seed=42):
    """Monte Carlo distribution of the Lilliefors statistic under H0.

    For each simulated standard-normal sample of size n, standardise it with its
    own mean and std (that is what makes this the Lilliefors test, not plain KS)
    and record the max ECDF deviation. Cached per sample size.
    """
    rng = np.random.default_rng(seed)
    sims = rng.standard_normal((n_sim, n))
    sims = (sims - sims.mean(axis=1, keepdims=True)) / sims.std(axis=1, ddof=1, keepdims=True)
    sims = np.sort(sims, axis=1)
    cdf = stats.norm.cdf(sims)
    i = np.arange(1, n + 1) / n
    j = np.arange(0, n) / n
    d = np.maximum((cdf - i).max(axis=1), (cdf - j).max(axis=1))
    return d


def lilliefors_test(x, alpha=0.05):
    """Lilliefors-corrected KS test for normality (mean & variance estimated from data).

    Returns (statistic, p-value, critical value). p-value and critical value are
    obtained from a Monte Carlo null distribution, which is accurate for any n.
    """
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    sd = x.std(ddof=1)
    z = (x - x.mean()) / (sd if sd > 0 else 1e-12)
    cdf = stats.norm.cdf(z)
    ecdf_hi = np.arange(1, n + 1) / n
    ecdf_lo = np.arange(0, n) / n
    d = max(np.max(np.abs(cdf - ecdf_hi)), np.max(np.abs(cdf - ecdf_lo)))

    null = lilliefors_null_dist(n)
    p = float((null >= d).mean())
    p = max(p, 1.0 / (len(null) + 1))          # avoid p = 0
    crit = float(np.quantile(null, 1 - alpha))
    return d, p, crit


def run_all_tests(x, alpha=0.05):
    results = []
    # Shapiro-Wilk
    sw = stats.shapiro(x)
    results.append({
        "Test": "Shapiro-Wilk",
        "Statistic": sw.statistic,
        "p-value": sw.pvalue,
        "Critical value": "—",
        f"Normal at α={alpha}": "Yes" if sw.pvalue > alpha else "No",
    })
    # Kolmogorov-Smirnov (Lilliefors)
    d, p, crit = lilliefors_test(x, alpha)
    results.append({
        "Test": "Kolmogorov-Smirnov (Lilliefors)",
        "Statistic": d,
        "p-value": p,
        "Critical value": f"{crit:.4f}",
        f"Normal at α={alpha}": "Yes" if d <= crit else "No",
    })
    # Anderson-Darling
    ad = stats.anderson(x, dist="norm")
    # significance levels for normal dist: 15, 10, 5, 2.5, 1
    levels = {15: 0, 10: 1, 5: 2, 2.5: 3, 1: 4}
    lvl = min(levels.keys(), key=lambda k: abs(k - alpha * 100))
    crit_ad = ad.critical_values[levels[lvl]]
    results.append({
        "Test": "Anderson-Darling",
        "Statistic": ad.statistic,
        "p-value": "—",
        "Critical value": f"{crit_ad:.4f} (at {lvl}%)",
        f"Normal at α={alpha}": "Yes" if ad.statistic < crit_ad else "No",
    })
    return pd.DataFrame(results)


def descriptive_stats(x):
    skew = stats.skew(x)
    kurt = stats.kurtosis(x)  # excess
    return pd.Series({
        "n": len(x),
        "Mean": np.mean(x),
        "Median": np.median(x),
        "Std Dev": np.std(x, ddof=1),
        "Min": np.min(x),
        "Max": np.max(x),
        "Skewness": skew,
        "Excess Kurtosis": kurt,
    })


def plot_all(x, col):
    with col:
        st.subheader("Histogram + fitted Normal")
        fig, ax = plt.subplots()
        ax.hist(x, bins="auto", density=True, color="#4c8bf5", alpha=0.7, edgecolor="white")
        grid = np.linspace(x.min(), x.max(), 300)
        ax.plot(grid, stats.norm.pdf(grid, x.mean(), x.std(ddof=1)), "r-", lw=2, label="Normal fit")
        ax.legend()
        st.pyplot(fig)

        st.subheader("Q-Q Plot")
        fig2, ax2 = plt.subplots()
        stats.probplot(x, dist="norm", plot=ax2)
        ax2.get_lines()[0].set(marker="o", markersize=4, color="#4c8bf5")
        ax2.get_lines()[1].set(color="crimson")
        st.pyplot(fig2)


# ----------------------------- App -----------------------------

st.title("📊 Normality Testing Dashboard")
st.write("Test whether your data is normally distributed using **Shapiro-Wilk**, "
         "**Kolmogorov-Smirnov (Lilliefors)**, and **Anderson-Darling** tests.")

# Sidebar
with st.sidebar:
    st.header("Data Source")
    source = st.radio("Choose data source",
                      ["Upload CSV", "Simulated data", "Paste values"])

    alpha = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01)

    data = None
    if source == "Upload CSV":
        f = st.file_uploader("CSV with numeric column", type=["csv"])
        if f is not None:
            df = pd.read_csv(f)
            num_cols = df.select_dtypes(include=np.number).columns.tolist()
            if num_cols:
                col = st.selectbox("Column to test", num_cols)
                data = df[col].dropna().values
            else:
                st.error("No numeric columns found.")
    elif source == "Simulated data":
        dist = st.selectbox("Distribution",
                            ["Normal", "Uniform", "Exponential", "Log-normal", "Bimodal (mix)"])
        n = st.slider("Sample size", 10, 2000, 300)
        rng = np.random.default_rng(42)
        if dist == "Normal":
            data = rng.normal(0, 1, n)
        elif dist == "Uniform":
            data = rng.uniform(-1, 1, n)
        elif dist == "Exponential":
            data = rng.exponential(1, n)
        elif dist == "Log-normal":
            data = rng.lognormal(0, 1, n)
        else:
            data = np.concatenate([rng.normal(-2, 0.8, n // 2),
                                   rng.normal(2, 0.8, n - n // 2)])
    else:  # paste values
        txt = st.text_area("Paste numeric values (comma/space/newline separated)")
        if txt.strip():
            try:
                data = np.array([float(v) for v in txt.replace(",", " ").split()])
            except ValueError:
                st.error("Could not parse all values as numbers.")

if data is None or len(data) < 8:
    st.info("👈 Provide data via the sidebar (CSV upload, simulation, or paste). "
            "At least 8 observations are required.")
    st.stop()

x = np.asarray(data, dtype=float)
x = x[np.isfinite(x)]
if len(x) < 8:
    st.error("Not enough valid numeric observations.")
    st.stop()

# Results
res_col, desc_col = st.columns([3, 2])

with res_col:
    st.subheader(f"Test Results (α = {alpha})")
    results = run_all_tests(x, alpha)

    def color_row(row):
        verdict = row.iloc[4]
        if verdict == "Yes":
            return ["color: #0a7d32"] * 5
        if verdict == "No":
            return ["color: #b3261e"] * 5
        return [""] * 5

    def fmt_stat(v):
        return f"{v:.4f}" if isinstance(v, (int, float)) and not pd.isna(v) else str(v)

    def fmt_p(v):
        if isinstance(v, (int, float)) and not pd.isna(v):
            return f"{v:.4g}" if v >= 1e-4 else f"{v:.2e}"
        return str(v)

    styled = results.style.apply(color_row, axis=1).format(
        {"Statistic": fmt_stat, "p-value": fmt_p}
    )
    st.dataframe(styled, use_container_width=True)

    with st.expander("How to read these tests"):
        st.markdown("""
- **Shapiro–Wilk**: best all-round test for n ≤ 5000. Low W / p < α ⇒ non-normal.
- **Kolmogorov–Smirnov (Lilliefors)**: compares the empirical CDF to the fitted
  normal CDF. The plain KS test assumes known parameters; Lilliefors corrects
  for estimated mean/variance. Statistic ≤ critical value ⇒ normal.
- **Anderson–Darling**: gives more weight to the tails. Statistic < critical
  value at your significance level ⇒ normal.
- Rule of thumb: **Shapiro–Wilk** for small-to-moderate samples, **Anderson–Darling**
  when tails matter, and report at least two tests together with Q-Q plots.
        """)

with desc_col:
    st.subheader("Descriptive Statistics")
    st.dataframe(descriptive_stats(x).to_frame("Value"), use_container_width=True)
    verdict = "✅ Consistent with normality" if (results.iloc[:, 4] == "Yes").sum() >= 2 else "⚠️ Data likely non-normal"
    st.metric("Overall verdict", verdict)

st.divider()
c1, c2 = st.columns(2)
c1.subheader("Histogram + Normal fit")
c2.subheader("Q-Q Plot")
fig, ax = plt.subplots()
ax.hist(x, bins="auto", density=True, color="#4c8bf5", alpha=0.7, edgecolor="white")
grid = np.linspace(x.min(), x.max(), 300)
ax.plot(grid, stats.norm.pdf(grid, x.mean(), x.std(ddof=1)), "r-", lw=2, label="Normal fit")
ax.legend()
c1.pyplot(fig)
fig2, ax2 = plt.subplots()
stats.probplot(x, dist="norm", plot=ax2)
ax2.get_lines()[0].set(marker="o", markersize=4, color="#4c8bf5")
ax2.get_lines()[1].set(color="crimson")
c2.pyplot(fig2)

st.caption("Tip: use simulated non-normal distributions to see how each test behaves.")
