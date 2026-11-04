import streamlit as st
import numpy as np
from scipy import stats

st.set_page_config(page_title="One-Sample T-Test", page_icon="☕", layout="centered")

st.title("☕ One-Sample T-Test")
st.caption("Test whether your sample's mean differs from a claimed / hypothesized value.")

# ---------- Inputs ----------
sample_input = st.text_area(
    "Sample data",
    value="248, 251, 244, 255, 249, 247, 252, 243, 250, 246",
    help="Comma- or space-separated numbers.",
)

mu0 = st.number_input(
    "Hypothesized mean (μ₀)",
    value=250.0,
    step=0.1,
    format="%.2f",
    help="The claimed / hypothesized population mean under H0.",
)

alpha = st.slider(
    "Significance level (α)",
    min_value=0.01,
    max_value=0.20,
    value=0.05,
    step=0.01,
    format="%.2f",
)

alternative = st.radio(
    "Alternative hypothesis",
    options=["two-sided", "less", "greater"],
    index=0,
    horizontal=True,
    help=(
        "**two-sided**: mean ≠ μ₀ · "
        "**less**: mean < μ₀ · "
        "**greater**: mean > μ₀"
    ),
)

# ---------- Parsing & validation ----------
def parse_numbers(text: str) -> np.ndarray | None:
    try:
        return np.array([float(x) for x in text.replace(",", " ").split()])
    except ValueError:
        return None

sample = parse_numbers(sample_input)

if sample is None:
    st.error("Please enter valid numbers (comma- or space-separated).")
    st.stop()

if len(sample) < 2:
    st.error("Need at least 2 observations.")
    st.stop()

if not np.all(np.isfinite(sample)):
    st.error("All values must be finite numbers.")
    st.stop()

if np.std(sample, ddof=1) == 0:
    st.error("Sample has zero variance — the t-test is undefined.")
    st.stop()

# ---------- Computation ----------
result = stats.ttest_1samp(sample, popmean=mu0, alternative=alternative)
t_stat = float(result.statistic)
p_value = float(result.pvalue)

n = len(sample)
dof = n - 1
mean = float(sample.mean())
sem = stats.sem(sample)  # standard error of the mean

# Critical value(s) and rejection region
if alternative == "two-sided":
    t_crit = stats.t.ppf(1 - alpha / 2, dof)
    reject = abs(t_stat) > t_crit
    region = f"|t| > {t_crit:.4f}"
elif alternative == "less":
    t_crit = stats.t.ppf(alpha, dof)
    reject = t_stat < t_crit
    region = f"t < {t_crit:.4f}"
else:  # greater
    t_crit = stats.t.ppf(1 - alpha, dof)
    reject = t_stat > t_crit
    region = f"t > {t_crit:.4f}"

# 95% confidence interval for the true mean
ci_low, ci_high = stats.t.interval(0.95, dof, loc=mean, scale=sem)

# ---------- Results ----------
st.subheader("Results")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Sample mean", f"{mean:.2f}")
m2.metric("t-statistic", f"{t_stat:.4f}")
m3.metric("p-value", f"{p_value:.4f}")
m4.metric("dof", dof, f"n = {n}")

st.info(
    f"**95% confidence interval for the true mean: "
    f"({ci_low:.2f}, {ci_high:.2f})** "
    f"(standard error = {sem:.4f})"
)

if reject:
    st.error(
        f"**Reject H0** — t = {t_stat:.4f} falls in the rejection region ({region}) "
        f"and p = {p_value:.4f} < α = {alpha:.2f}. "
        f"The true mean differs from μ₀ = {mu0:.2f}."
    )
else:
    st.success(
        f"**Fail to reject H0** — t = {t_stat:.4f} is outside the rejection region ({region}) "
        f"and p = {p_value:.4f} ≥ α = {alpha:.2f}. "
        f"No evidence that the mean differs from μ₀ = {mu0:.2f}."
    )

st.caption(
    f"t = (x̄ − μ₀) / SE = ({mean:.2f} − {mu0:.2f}) / {sem:.4f} = {t_stat:.4f} · "
    f"dof = n − 1 = {dof}"
)

# ---------- Visualization ----------
st.subheader("Sample vs Hypothesized Mean")

chart_data = {
    "Source": ["Sample mean", "Hypothesized μ₀"],
    "Value": [mean, mu0],
}
st.bar_chart(chart_data, x="Source", y="Value", height=300)

with st.expander("Sample distribution (strip view)"):
    strip_df = {"Observation index": range(1, n + 1), "Value": sample}
    st.line_chart(strip_df, x="Observation index", y="Value", height=250)
    st.caption(
        f"Horizontal reference: μ₀ = {mu0:.2f} · "
        f"sample std dev = {sample.std(ddof=1):.2f}"
    )

with st.expander("Effect size (Cohen's d)"):
    s = sample.std(ddof=1)
    d = (mean - mu0) / s
    st.write(f"Cohen's d = **{d:.3f}**")
    st.caption(
        "Rule of thumb: |d| ≈ 0.2 small · ≈ 0.5 medium · ≈ 0.8 large. "
        "Statistical significance ≠ practical importance — a large n can make a "
        "tiny difference 'significant' (as we discussed)."
    )
