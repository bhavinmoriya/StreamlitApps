"""
Streamlit App: Bayesian Polynomial Regression with Interactive Plotly Plots
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from numpy.linalg import inv

# Helper Functions
def design_matrix(x, deg):
    x = np.asarray(x)
    return np.vstack([x**i for i in range(deg+1)]).T

def bayesian_posterior(x, y, deg, alpha=1.0, beta=50.0):
    X = design_matrix(x, deg)
    S0_inv = alpha * np.eye(deg+1)
    SN_inv = S0_inv + beta * X.T @ X
    SN = inv(SN_inv)
    mN = beta * SN @ X.T @ y
    return mN, SN

def true_poly_func(x, coeffs):
    x = np.asarray(x)
    result = np.zeros_like(x, dtype=float)
    for i in range(len(coeffs)):
        result += coeffs[i] * x**i
    return result

# Page config
st.set_page_config(page_title="Bayesian Polynomial Regression", layout="wide")

st.title("🔮 Bayesian Polynomial Regression")
st.markdown("""
This app demonstrates **Bayesian updating** for polynomial regression:
- Choose polynomial degree and coefficients
- Generate synthetic data points
- Sequentially add points (5 → 6 → 7 → 8 → 9 → 10)
- Use **Bayes' theorem** to update coefficient estimates
- See how predictions improve with more evidence!
""")

# Sidebar: Input Parameters
st.sidebar.header("🎯 Polynomial Settings")

deg = st.sidebar.number_input(
    "Polynomial Degree",
    min_value=1,
    max_value=10,
    value=3,
)

st.sidebar.subheader("True Polynomial Coefficients")
coeffs = []
for i in range(deg+1):
    coef_val = st.sidebar.number_input(
        f"a{i} (x^{i})",
        min_value=-10.0,
        max_value=10.0,
        value=1.0 if i == 0 else (-2.0 if i == 1 else (0.5 if i == 2 else (3.0 if i == 3 else 0.0))),
        step=0.1,
    )
    coeffs.append(coef_val)
coeffs = np.array(coeffs)

noise_std = st.sidebar.number_input(
    "Noise Standard Deviation",
    min_value=0.01,
    max_value=1.0,
    value=0.1,
    step=0.01,
)

alpha = st.sidebar.number_input("Prior variance scale (α)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
beta = st.sidebar.number_input("Inverse noise variance (β)", min_value=1.0, max_value=100.0, value=50.0, step=1.0)

# Generate Synthetic Data
np.random.seed(42)
n_total = 10
x_all = np.linspace(0, 1, n_total)
y_all = true_poly_func(x_all, coeffs) + np.random.normal(0, noise_std, size=n_total)

# Show data points
st.header("📈 Data Points")
df_points = pd.DataFrame({"x": x_all, "y": y_all})
st.dataframe(df_points, use_container_width=True)

fig_points = go.Figure()
fig_points.add_trace(go.Scatter(x=x_all, y=y_all, mode="markers", name="Data Points", marker=dict(size=12, color="blue", opacity=0.7)))
fig_points.add_trace(go.Scatter(x=x_all, y=true_poly_func(x_all, coeffs), mode="lines", name="True Polynomial", line=dict(color="green", width=2)))
fig_points.update_layout(title="Generated Data Points vs True Polynomial", xaxis_title="x", yaxis_title="y", hovermode="x unified")
st.plotly_chart(fig_points, use_container_width=True)

# Bayesian Updating
st.header("🔬 Bayesian Updating (5 → 6 → 7 → 8 → 9 → 10 Points)")

results = []
x_grid = np.linspace(0, 1, 200)

for n in range(5, n_total+1):
    x_n = x_all[:n]
    y_n = y_all[:n]
    mN, SN = bayesian_posterior(x_n, y_n, deg=deg, alpha=alpha, beta=beta)
    
    est_y = np.zeros_like(x_grid)
    for i in range(deg+1):
        est_y += mN[i] * x_grid**i
    
    true_y = true_poly_func(x_grid, coeffs)
    coef_error = np.linalg.norm(mN - coeffs)
    
    results.append({"n_points": n, "coeffs": mN, "est_y": est_y, "true_y": true_y, "coef_error": coef_error, "SN": SN})

# Plot All 6 Plots
st.header("📊 Evolution of Polynomial Fit (All 6 Plots)")

for i, res in enumerate(results):
    n = res["n_points"]
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=x_all[:n], y=y_all[:n], mode="markers", name="Data Points", marker=dict(size=10, color="blue", opacity=0.8)))
    fig.add_trace(go.Scatter(x=x_grid, y=res["est_y"], mode="lines", name="Estimated Polynomial", line=dict(color="red", width=3)))
    fig.add_trace(go.Scatter(x=x_grid, y=res["true_y"], mode="lines", name="True Polynomial", line=dict(color="green", width=2, dash="dash")))
    
    fig.update_layout(title=f"n = {n} Points", xaxis_title="x", yaxis_title="y", hovermode="x unified", height=300, showlegend=False)
    st.subheader(f"Plot {i+1}: {n} Points")
    st.plotly_chart(fig, use_container_width=True)

# Coefficient Table
st.header("📋 Coefficient Estimates vs True Values")

coef_table = pd.DataFrame({
    "n_points": [r["n_points"] for r in results],
    **{f"a{i}_est": [r["coeffs"][i] for r in results] for i in range(deg+1)},
    **{f"a{i}_true": [coeffs[i] for _ in results] for i in range(deg+1)},
    "coef_error": [r["coef_error"] for r in results]
})
st.dataframe(coef_table, use_container_width=True)

# Error Plot
st.header("📉 Coefficient Error vs Number of Points")

fig_error = go.Figure()
fig_error.add_trace(go.Scatter(x=[r["n_points"] for r in results], y=[r["coef_error"] for r in results], mode="lines+markers", name="Coefficient Error", marker=dict(size=10, color="orange"), line=dict(width=3)))
fig_error.update_layout(title="L2 Error in Coefficients (Decreases as More Points Added)", xaxis_title="Number of Points", yaxis_title="Coefficient Error (L2)", hovermode="x unified")
st.plotly_chart(fig_error, use_container_width=True)

# Explanation
st.header("🧠 Why This Works: Bayes' Theorem")

st.markdown("""
**Bayes' Theorem for Polynomial Regression:**

$$p(\mathbf{w} | \text{data}) = \\frac{p(\text{data} | \mathbf{w}) \\cdot p(\mathbf{w})}{p(\text{data})}$$

**Key Insight:**
- Each new point updates the posterior
- Posterior becomes **tighter** (less uncertainty) with more data
- Posterior mean becomes **closer** to true coefficients
- This is exactly "more evidence → better posterior"!
""")

st.success("✅ Your idea is correct: More points → Better polynomial coefficients via Bayes' theorem!")

linkedin_url = "https://www.linkedin.com/in/bhavin-moriya-ph-d-b0b88b2/"
github_url = "https://github.com/bhavinmoriya"

st.markdown("## Connect with me")

col1, col2 = st.columns(2)

with col1:
    st.link_button("🔗 Follow on LinkedIn", linkedin_url)

with col2:
    st.link_button("💻 Follow on GitHub", github_url)
