import streamlit as st
import numpy as np
from scipy import stats

st.set_page_config(page_title="T-Test App", layout="centered")
st.title("T-Test App with Levene's Test")

st.write("Enter numbers as comma-separated values, for example: 1, 2, 3, 4, 5")

def parse_numbers(text):
    try:
        arr = np.array([float(x.strip()) for x in text.split(",") if x.strip() != ""])
        return arr
    except Exception:
        return None

def decision(p_value, alpha):
    return "Reject the null hypothesis." if p_value < alpha else "Fail to reject the null hypothesis."

test_type = st.selectbox(
    "Choose test type",
    ["One-sample t-test", "Two-sample t-test"]
)

alpha = st.number_input(
    "Significance level (alpha)",
    min_value=0.0001,
    max_value=0.5,
    value=0.05,
    step=0.01
)

side = st.radio(
    "Choose alternative hypothesis",
    ["Two-sided", "One-sided (greater)", "One-sided (less)"]
)

alternative_map = {
    "Two-sided": "two-sided",
    "One-sided (greater)": "greater",
    "One-sided (less)": "less"
}
alternative = alternative_map[side]

st.subheader("Null hypothesis")

if test_type == "One-sample t-test":
    st.write("H0: the population mean equals the hypothesized mean, μ = μ0.")
else:
    st.write("H0: the two population means are equal, μ1 = μ2.")

if test_type == "One-sample t-test":
    sample_text = st.text_area("Enter sample data", height=120)
    mu0 = st.number_input("Hypothesized mean (μ0)", value=0.0)

    st.latex(r"t = \frac{\bar{x} - \mu_0}{s / \sqrt{n}}")

    if st.button("Run test"):
        x = parse_numbers(sample_text)
        if x is None or len(x) < 2:
            st.error("Please enter at least two valid numbers.")
        else:
            t_stat, p_value = stats.ttest_1samp(x, popmean=mu0, alternative=alternative)

            st.subheader("Results")
            st.write(f"t-statistic: {t_stat:.6f}")
            st.write(f"p-value: {p_value:.6f}")
            st.write(f"Decision: {decision(p_value, alpha)}")

else:
    group1_text = st.text_area("Enter group 1 data", height=120)
    group2_text = st.text_area("Enter group 2 data", height=120)

    st.markdown("### Formulas")
    st.latex(r"\text{Levene test: } H_0 : \sigma_1^2 = \sigma_2^2")
    st.latex(r"\text{If equal variances: } t = \frac{\bar{X}_1 - \bar{X}_2}{s_p \sqrt{\frac{1}{n_1}+\frac{1}{n_2}}}")
    st.latex(r"\text{If unequal variances: } t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{\frac{s_1^2}{n_1}+\frac{s_2^2}{n_2}}}")

    if st.button("Run test"):
        x1 = parse_numbers(group1_text)
        x2 = parse_numbers(group2_text)

        if x1 is None or x2 is None or len(x1) < 2 or len(x2) < 2:
            st.error("Please enter at least two valid numbers in each group.")
        else:
            levene_stat, levene_p = stats.levene(x1, x2, center="median")

            st.subheader("Levene's test")
            st.write(f"Levene statistic: {levene_stat:.6f}")
            st.write(f"Levene p-value: {levene_p:.6f}")

            if levene_p < alpha:
                st.write("Decision on variances: Reject H0. Variances are significantly different.")
                equal_var = False
            else:
                st.write("Decision on variances: Fail to reject H0. Variances can be treated as equal.")
                equal_var = True

            t_stat, p_value = stats.ttest_ind(
                x1,
                x2,
                equal_var=equal_var,
                alternative=alternative
            )

            st.subheader("t-test results")
            st.write(f"t-statistic: {t_stat:.6f}")
            st.write(f"p-value: {p_value:.6f}")
            st.write(f"Decision: {decision(p_value, alpha)}")

linkedin_url = "https://www.linkedin.com/in/bhavin-moriya-ph-d-b0b88b2/"
github_url = "https://github.com/bhavinmoriya"

st.markdown("## Connect with me")

col1, col2 = st.columns(2)

with col1:
    st.link_button("🔗 Follow on LinkedIn", linkedin_url)

with col2:
    st.link_button("💻 Follow on GitHub", github_url)
