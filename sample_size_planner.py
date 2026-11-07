import streamlit as st
from statsmodels.stats.power import TTestPower

st.set_page_config(page_title="Sample Size Planner", page_icon="📊", layout="centered")

st.title("📊 Sample Size Planner")
st.caption("Power analysis for a one-sample t-test")

with st.sidebar:
    st.header("Design inputs")
    mu0 = st.number_input("Null-hypothesis mean (μ₀)", value=10.0, help="The reference value being tested.")
    meaningful_difference = st.number_input(
        "Minimum meaningful difference (Δ)",
        min_value=0.000001,
        value=1.0,
        help="Smallest difference from μ₀ that you want the study to reliably detect. Enter a positive magnitude."
    )
    sigma = st.number_input(
        "Estimated population standard deviation (σ)",
        min_value=0.000001,
        value=2.0,
        help="Estimate from prior research, a pilot study, or subject-matter knowledge."
    )
    alpha = st.select_slider(
        "Significance level (α)",
        options=[0.01, 0.025, 0.05, 0.10],
        value=0.05,
        format_func=lambda x: f"{x:.1%}"
    )
    power = st.select_slider(
        "Desired statistical power (1 − β)",
        options=[0.70, 0.80, 0.85, 0.90, 0.95, 0.99],
        value=0.80,
        format_func=lambda x: f"{x:.0%}"
    )
    alternative = st.radio(
        "Alternative hypothesis",
        ["Two-sided (μ ≠ μ₀)", "One-sided (μ > μ₀ or μ < μ₀)"],
        index=0,
        help="Choose one-sided only if the direction is scientifically justified and decided before seeing the data."
    )

tail = "two-sided" if alternative.startswith("Two-sided") else "larger"
effect_size = meaningful_difference / sigma

# statsmodels computes the sample size from standardized effect size,
# significance level, desired power, and alternative.
analysis = TTestPower()
n_raw = analysis.solve_power(
    effect_size=effect_size,
    power=power,
    alpha=alpha,
    alternative=tail
)
n = int(__import__("math").ceil(n_raw))

st.subheader("Recommended sample size")
c1, c2, c3 = st.columns(3)
c1.metric("Required n", f"{n}")
c2.metric("Standardized effect (d)", f"{effect_size:.3f}")
c3.metric("Target power", f"{power:.0%}")

st.success(
    f"Plan for **at least {n} independent observations** to target "
    f"{power:.0%} power at α = {alpha:.1%}, assuming the effect and variability "
    f"entered above are reasonable."
)

st.markdown("### Hypotheses")
if alternative.startswith("Two-sided"):
    st.latex(r"H_0: \mu = \mu_0")
    st.latex(r"H_1: \mu \ne \mu_0")
else:
    st.info("For a one-sided test, specify the direction in the research protocol.")
    st.latex(r"H_0: \mu = \mu_0")
    st.latex(r"H_1: \mu > \mu_0 \quad \text{or} \quad \mu < \mu_0")

st.markdown("### How the calculation works")
st.latex(r"d = \frac{\Delta}{\sigma}")
st.write(
    "The sample size is driven by the standardized effect size "
    r"$d=\Delta/\sigma$, significance level α, desired power, and tail choice. "
    "The app rounds up because a fractional participant cannot be sampled."
)

with st.expander("Interpretation and cautions"):
    st.markdown(
        """
        - **Δ (meaningful difference):** the effect you want the study to be able to detect—not an effect chosen after looking at the results.
        - **σ (standard deviation):** should come from relevant prior data or a pilot study; uncertainty in this estimate may warrant a conservative choice.
        - **Power:** 80% means that, if the true effect is the specified Δ and assumptions hold, the planned test has about an 80% chance of rejecting the null.
        - **α:** controls the Type I error probability for the planned test under its assumptions.
        - **Independent observations:** this calculation assumes independent, identically distributed observations and a one-sample t-test framework.
        - **No optional stopping:** do not repeatedly check ordinary p-values and stop at significance. If you plan interim looks, use a sequential/group-sequential design with error control.
        - **More than n:** collecting additional observations is not automatically invalid, but the sampling and analysis plan should be prespecified. Avoid deciding to add data based on whether the current p-value is significant.
        - **Population size:** this calculation does not apply a finite-population correction. For sampling a substantial fraction of a small finite population, a different design calculation may be needed.
        - **One-sided test:** only choose it when the directional claim is justified in advance.
        """
    )

st.caption(
    "This is a planning aid, not a substitute for a study-specific design. "
    "It calculates sample size for a one-sample t-test; it does not prove that a hypothesis is true or false."
)
