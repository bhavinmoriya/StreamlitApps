import numpy as np
import polars as pl
import matplotlib.pyplot as plt
import streamlit as st
from scipy.stats import beta

st.set_page_config(
    page_title="Bayesian Beta Distribution Explorer",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Bayesian Beta Distribution Explorer")

st.markdown(
    """
Move the sliders to see how changing **α (alpha)** and **β (beta)**
changes your belief about an unknown probability θ.
"""
)

# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.header("Beta Parameters")

alpha = st.sidebar.slider(
    "Alpha (α)",
    min_value=1,
    max_value=50,
    value=2,
)

beta_param = st.sidebar.slider(
    "Beta (β)",
    min_value=1,
    max_value=50,
    value=2,
)

# -----------------------------
# Statistics
# -----------------------------

mean = alpha / (alpha + beta_param)

variance = (
    alpha * beta_param
    / (
        (alpha + beta_param) ** 2
        * (alpha + beta_param + 1)
    )
)

mode = None
if alpha > 1 and beta_param > 1:
    mode = (alpha - 1) / (alpha + beta_param - 2)

# -----------------------------
# Density
# -----------------------------

theta = np.linspace(0.001, 0.999, 1000)

density = beta.pdf(theta, alpha, beta_param)

df = pl.DataFrame(
    {
        "theta": theta,
        "density": density,
    }
)

# -----------------------------
# Plot
# -----------------------------

fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(
    df["theta"],
    df["density"],
    linewidth=3,
)

ax.axvline(
    mean,
    linestyle="--",
    label=f"Mean = {mean:.3f}",
)

if mode is not None:
    ax.axvline(
        mode,
        linestyle=":",
        label=f"Mode = {mode:.3f}",
    )

ax.set_xlabel("θ")
ax.set_ylabel("Density")
ax.set_title(f"Beta({alpha}, {beta_param})")
ax.grid(alpha=0.3)
ax.legend()

st.pyplot(fig)

# -----------------------------
# Statistics
# -----------------------------

c1, c2, c3 = st.columns(3)

c1.metric("Mean", f"{mean:.4f}")

if mode is None:
    c2.metric("Mode", "Undefined")
else:
    c2.metric("Mode", f"{mode:.4f}")

c3.metric("Variance", f"{variance:.5f}")

# -----------------------------
# Interpretation
# -----------------------------

st.subheader("Interpretation")

st.write(
    f"""
Your current prior belief is **Beta({alpha}, {beta_param})**.

This means you believe the unknown probability θ is most likely
around **{mean:.3f}**, although values nearby are also plausible.

The curve is **not** the probability of θ.
Instead, it describes **how plausible each possible value of θ is**.
"""
)

st.info(
    "Think of the curve as a 'belief landscape'. "
    "Tall regions indicate more plausible values of θ."
)

# -----------------------------
# Probability Calculator
# -----------------------------

st.subheader("Probability Calculator")

left, right = st.columns(2)

a = left.slider(
    "Lower θ",
    0.0,
    1.0,
    0.40,
)

b = right.slider(
    "Upper θ",
    0.0,
    1.0,
    0.60,
)

if a > b:
    a, b = b, a

probability = beta.cdf(b, alpha, beta_param) - beta.cdf(
    a,
    alpha,
    beta_param,
)

st.success(
    f"P({a:.2f} ≤ θ ≤ {b:.2f}) = {probability:.4f}"
)

# -----------------------------
# Sample pseudo-observations
# -----------------------------

st.subheader("Pseudo-observation intuition")

st.write(
    f"""
A Beta({alpha}, {beta_param}) prior behaves roughly like:

- Prior successes ≈ **{alpha-1}**
- Prior failures ≈ **{beta_param-1}**

These are called **pseudo-observations** because they summarize your
belief before seeing new data.
"""
)
