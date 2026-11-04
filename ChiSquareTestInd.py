import streamlit as st
import numpy as np
import pandas as pd
from scipy.stats import chi2, chi2_contingency

st.set_page_config(page_title="Chi-Square Independence Test", page_icon="🧮", layout="centered")

st.title("🧮 Chi-Square Test of Independence")
st.caption("Check whether two categorical variables are related, from a contingency table.")

# ---------- Input ----------
st.subheader("Contingency Table")
row_labels_raw = st.text_input(
    "Row labels (optional)",
    value="Male, Female",
    help="Comma-separated labels for each row. Leave blank for Row 1, Row 2, ..."
)
col_labels_raw = st.text_input(
    "Column labels (optional)",
    value="Buy, No Buy",
    help="Comma-separated labels for each column. Leave blank for Col 1, Col 2, ..."
)

row_labels = [s.strip() for s in row_labels_raw.split(",") if s.strip()]
col_labels = [s.strip() for s in col_labels_raw.split(",") if s.strip()]

default_table = pd.DataFrame(
    [[30, 10], [20, 40]],
    index=row_labels or None,
    columns=col_labels or None,
)

table = st.data_editor(
    default_table,
    num_rows="dynamic",
    use_container_width=True,
    key="contingency_editor",
)

alpha = st.slider(
    "Significance level (α)",
    min_value=0.01,
    max_value=0.20,
    value=0.05,
    step=0.01,
    format="%.2f",
)

# ---------- Validation ----------
observed = table.to_numpy(dtype=float)

if observed.ndim != 2 or observed.shape[0] < 2 or observed.shape[1] < 2:
    st.error("The table needs at least 2 rows and 2 columns.")
    st.stop()

if not np.all(np.isfinite(observed)) or np.any(observed < 0):
    st.error("All cells must be non-negative numbers.")
    st.stop()

row_totals = observed.sum(axis=1)
col_totals = observed.sum(axis=0)
if np.any(row_totals == 0) or np.any(col_totals == 0):
    st.error("Every row and every column must have at least one observation.")
    st.stop()

# ---------- Computation ----------
chi2_stat, p_value, dof, expected = chi2_contingency(observed)
critical = chi2.ppf(1 - alpha, dof)
reject = chi2_stat > critical

# ---------- Results ----------
st.subheader("Results")

m1, m2, m3, m4 = st.columns(4)
m1.metric("χ² statistic", f"{chi2_stat:.4f}")
m2.metric("p-value", f"{p_value:.6e}")
m3.metric("Degrees of Freedom", int(dof))
m4.metric("Critical Value", f"{critical:.4f}", f"α = {alpha:.2f}")

if reject:
    st.error(
        f"**Reject H0** — χ² = {chi2_stat:.4f} > {critical:.4f} "
        f"(p = {p_value:.6e} < α = {alpha:.2f}). "
        "Evidence that the two variables are **related**."
    )
else:
    st.success(
        f"**Fail to reject H0** — χ² = {chi2_stat:.4f} ≤ {critical:.4f} "
        f"(p = {p_value:.6e} ≥ α = {alpha:.2f}). "
        "No evidence of a relationship; the variables appear **independent**."
    )

st.caption(
    f"dof = (rows − 1) × (cols − 1) = "
    f"({observed.shape[0]} − 1) × ({observed.shape[1]} − 1) = {int(dof)}"
)

# ---------- Expected table ----------
st.subheader("Expected Counts (under independence)")
exp_index = table.index.tolist() if table.index is not None else None
exp_cols = table.columns.tolist() if table.columns is not None else None
exp_df = pd.DataFrame(expected, index=exp_index, columns=exp_cols).round(2)
st.dataframe(exp_df, use_container_width=True)

# ---------- Per-cell contributions ----------
with st.expander("Per-cell contributions (O − E)² / E"):
    contrib = (observed - expected) ** 2 / expected
    contrib_df = pd.DataFrame(
        contrib.round(3),
        index=exp_index,
        columns=exp_cols,
    )
    st.dataframe(contrib_df, use_container_width=True)
    st.caption(f"Sum of all contributions = χ² = {chi2_stat:.4f}")
    low_exp = (expected < 5).sum()
    if low_exp > 0:
        st.warning(
            f"{low_exp} expected count(s) are below 5. "
            "The chi-square approximation may be unreliable — consider "
            "Fisher's exact test (scipy.stats.fisher_exact for 2×2)."
        )

# ---------- Visualization ----------
st.subheader("Observed Counts by Group")
plot_df = table.copy()
plot_df.index = table.index.astype(str)
plot_df.columns = table.columns.astype(str)
st.bar_chart(plot_df, x_label="Group", y_label="Count", stack=False)

with st.expander("Proportions within each row (%)"):
    props = plot_df.div(plot_df.sum(axis=1), axis=0) * 100
    st.bar_chart(props, x_label="Group", y_label="Percent", stack=False)
    st.caption("If the variables are independent, the bar patterns should look similar across rows.")
