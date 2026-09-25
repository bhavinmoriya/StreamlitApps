import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Normal QQ-Plot Explorer", layout="wide")
st.title("📊 Normal QQ-Plot Explorer")
st.markdown(
    "Select one or more distributions to see how their QQ-plots deviate from "
    "the normal reference line — the easiest way to build intuition for "
    "skewness and tail behaviour."
)

# ---------------------------------------------------------------
# Distribution catalogue
# ---------------------------------------------------------------
SEED = 42

DISTRIBUTIONS = {
    "Normal": {
        "sample": lambda n, rng: rng.normal(0, 1, n),
        "explanation": (
            "**Points fall on the straight reference line throughout.** "
            "The data is approximately normally distributed — this is your baseline."
        ),
        "hint": "On the line → normal",
    },
    "Right-skewed (e.g. lognormal / exponential-like)": {
        "sample": lambda n, rng: rng.lognormal(0, 0.8, n),
        "explanation": (
            "**Reverse S-shape: points dip below the line on the left, "
            "then curve upward above the line on the right.** "
            "The right tail is stretched: large values are more extreme than "
            "a normal allows. Typical for incomes, waiting times, sizes."
        ),
        "hint": "Curves up at the right end → heavy right tail",
    },
    "Left-skewed (e.g. negative lognormal)": {
        "sample": lambda n, rng: -rng.lognormal(0, 0.8, n),
        "explanation": (
            "**Mirrored S-shape: points bow above the line on the left, "
            "below on the right.** The left tail is stretched: small values "
            "are more extreme than a normal allows. Typical for bounded "
            "scores capped near a maximum."
        ),
        "hint": "Curves down at the left end → heavy left tail",
    },
    "Heavy tails (Student-t, df=3)": {
        "sample": lambda n, rng: rng.standard_t(3, n),
        "explanation": (
            "**Points follow the line in the middle but swing far off at BOTH "
            "extremes (above at right, below at left).** Outliers are much more "
            "frequent than under a normal — high kurtosis. Financial returns "
            "often look like this."
        ),
        "hint": "Off the line at both ends → heavy tails",
    },
    "Light tails (uniform-like)": {
        "sample": lambda n, rng: rng.uniform(-2, 2, n),
        "explanation": (
            "**Points hug the line in the middle but flatten out at the ends, "
            "staying inside where a normal would wander off.** Extremes are "
            "milder than a normal — data is more concentrated. Typical of "
            "bounded or measurement-clipped data."
        ),
        "hint": "Flat at the ends → light tails",
    },
    "Same shape, different mean & spread": {
        "sample": lambda n, rng: rng.normal(5, 3, n),
        "explanation": (
            "**Points stay perfectly linear but the line is shifted (different "
            "mean) and has a different slope (different variance).** "
            "The data is still normal — only the location and scale differ. "
            "QQ-plots are invariant to this once the reference line is fitted."
        ),
        "hint": "Straight, different intercept/slope → different μ and σ",
    },
}

# ---------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------
st.sidebar.header("Controls")

selected = st.sidebar.multiselect(
    "Select cases to plot",
    list(DISTRIBUTIONS.keys()),
    default=["Normal", "Right-skewed (e.g. lognormal / exponential-like)"],
)

n = st.sidebar.slider("Sample size", 50, 2000, 500, 50)

# Optional extra: overlay a comparison QQ-plot of a pure normal sample
show_band = st.sidebar.checkbox("Show 95% reference band (normal data envelope)", value=True)

if not selected:
    st.warning("Please select at least one case in the sidebar.")
    st.stop()

rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------
# Plot grid: histogram + QQ-plot side by side for each case
# ---------------------------------------------------------------
cols_per_case = 2  # histogram | QQ-plot

ncases = len(selected)
fig, axes = plt.subplots(
    ncases, cols_per_case,
    figsize=(12, 4.2 * ncases),
    squeeze=False,
)

for i, name in enumerate(selected):
    data = DISTRIBUTIONS[name]["sample"](n, rng)

    ax_hist, ax_qq = axes[i][0], axes[i][1]

    # --- histogram ---
    ax_hist.hist(data, bins=40, density=True, color="#7fb3d5",
                 edgecolor="white", alpha=0.9)
    xs = np.linspace(data.min(), data.max(), 300)
    mu, sd = data.mean(), data.std(ddof=1)
    ax_hist.plot(xs, stats.norm.pdf(xs, mu, sd), "r--", lw=2,
                 label="fitted normal")
    ax_hist.set_title(f"{name}\n(histogram vs fitted normal)")
    ax_hist.legend(fontsize=8)

    # --- QQ plot ---
    (osm, osr), (slope, intercept, r) = stats.probplot(data, dist="norm")
    ax_qq.scatter(osm, osr, s=10, color="#2c3e50", alpha=0.6)
    fit_line = slope * osm + intercept
    ax_qq.plot(osm, fit_line, "r-", lw=2, label="reference line")

    if show_band:
        # Monte-Carlo envelope: how far normal samples of this size wander
        sims = np.array([
            np.sort(rng.normal(size=n)) for _ in range(100)
        ])
        lo = np.percentile(sims, 2.5, axis=0) * sd + mu
        hi = np.percentile(sims, 97.5, axis=0) * sd + mu
        order = np.argsort(osm)
        ax_qq.fill(np.concatenate([osm[order], osm[order][::-1]]),
                   np.concatenate([lo[order][::-1], hi[order]]),
                   color="green", alpha=0.15,
                   label="95% band for normal data")

    ax_qq.set_title(f"Normal QQ-plot — {name}")
    ax_qq.set_xlabel("Theoretical normal quantiles")
    ax_qq.set_ylabel("Sample quantiles")
    ax_qq.legend(fontsize=8)

fig.tight_layout()
st.pyplot(fig)

# ---------------------------------------------------------------
# Interpretation for each selected case
# ---------------------------------------------------------------
st.header("🔍 How to read each plot")
for name in selected:
    info = DISTRIBUTIONS[name]
    st.markdown(f"**{name}**  \n*Quick cue:* {info['hint']}")
    st.markdown(info["explanation"])
    st.markdown("---")

st.caption(
    "Tip: compare the shape of the points to the green band — inside the band, "
    "deviations are what you'd expect from genuinely normal data."
)
