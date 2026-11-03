import streamlit as st
import numpy as np
from scipy.stats import chi2

st.set_page_config(page_title="Chi-Square Goodness-of-Fit", page_icon="📊", layout="centered")

st.title("📊 Chi-Square Goodness-of-Fit Test")
st.caption("Compare observed counts against expected counts — no equal-sum assumption.")

# ---------- Inputs ----------
col1, col2 = st.columns(2)

with col1:
    observed_input = st.text_area(
        "Observed data",
        value="50, 10, 5, 20, 10, 55, 50",
        help="Comma- or space-separated counts.",
    )

with col2:
    expected_input = st.text_area(
        "Expected data",
        value="60, 10, 8, 10, 6, 26, 80",
        help="Comma- or space-separated counts. Must match observed length.",
    )

alpha = st.slider(
    "Significance level (α)",
    min_value=0.01,
    max_value=0.20,
    value=0.05,
    step=0.01,
    format="%.2f",
)

# ---------- Parsing & validation ----------
def parse_numbers(text: str) -> np.ndarray | None:
    try:
        values = np.array([float(x) for x in text.replace(",", " ").split()])
        return values
    except ValueError:
        return None

obs = parse_numbers(observed_input)
exp = parse_numbers(expected_input)

if obs is None or exp is None:
    st.error("Please enter valid numbers (comma- or space-separated).")
    st.stop()

if len(obs) != len(exp):
    st.error(f"Observed ({len(obs)}) and expected ({len(exp)}) must have the same length.")
    st.stop()

if len(obs) < 2:
    st.error("Need at least 2 categories.")
    st.stop()

if np.any(obs < 0) or np.any(exp <= 0):
    st.error("Observed must be ≥ 0 and expected must be > 0 for every category.")
    st.stop()

# ---------- Computation (manual, so sums need not match) ----------
chi2_stat = float(np.sum((obs - exp) ** 2 / exp))
dof = len(obs) - 1
p_value = float(chi2.sf(chi2_stat, dof))          # survival function = 1 - CDF
critical_value = float(chi2.ppf(1 - alpha, dof))
reject = chi2_stat > critical_value

# ---------- Results ----------
st.subheader("Results")

metric1, metric2, metric3 = st.columns(3)
metric1.metric("Chi-Square Statistic", f"{chi2_stat:.4f}")
metric2.metric("Critical Value", f"{critical_value:.4f}", f"α = {alpha:.2f}")
metric3.metric("Degrees of Freedom", dof)

st.metric("p-value", f"{p_value:.6e}")

if reject:
    st.error(
        f"**Reject the null hypothesis** — χ² = {chi2_stat:.4f} > "
        f"{critical_value:.4f} (p = {p_value:.6e} < α = {alpha:.2f}). "
        "Observed distribution differs from expected."
    )
else:
    st.success(
        f"**Fail to reject the null hypothesis** — χ² = {chi2_stat:.4f} ≤ "
        f"{critical_value:.4f} (p = {p_value:.6e} ≥ α = {alpha:.2f}). "
        "No significant difference detected."
    )

# ---------- Per-category breakdown ----------
st.subheader("Per-Category Contributions")
contrib = (obs - exp) ** 2 / exp
table_data = {
    "Category": range(1, len(obs) + 1),
    "Observed": obs,
    "Expected": exp,
    "(O−E)²/E": np.round(contrib, 4),
}
st.dataframe(table_data, use_container_width=True)

st.caption(f"Sum of contributions = χ² = {chi2_stat:.4f}")

# ---------- Visualization ----------
st.subheader("Observed vs Expected")

chart_data = {
    "Category": [str(i) for i in range(1, len(obs) + 1)],
    "Observed": obs,
    "Expected": exp,
}
st.bar_chart(chart_data, x="Category", y=["Observed", "Expected"])

# Optional: chi-square distribution with critical region
with st.expander("Chi-Square distribution & test statistic"):
    x = np.linspace(0, max(chi2_stat, critical_value) * 1.5, 300)
    density = chi2.pdf(x, dof)
    st.line_chart({"χ² distribution": density}, x=x, height=250)
    st.markdown(
        f"- Dashed reference: critical value = **{critical_value:.4f}** at α = {alpha:.2f}\n"
        f"- Test statistic: **{chi2_stat:.4f}** "
        f"({'right of' if reject else 'left of'} the critical value)"
    )
