import streamlit as st
from scipy.stats import hypergeom
import numpy as np

# Title and description
st.title("🎲 Lottery Probability Calculator")
st.markdown("""
This app calculates the probability of matching exactly **k** numbers (or up to **k** numbers) in a lottery draw.
- **N**: Total numbers in the pool (e.g., 50).
- **K**: Winning numbers drawn (e.g., 5).
- **n**: Your numbers (tickets) (e.g., 10).
- **k**: Matches you want to calculate for (e.g., 2).
""")

# Inputs
col1, col2 = st.columns(2)
with col1:
    N = st.number_input("Total numbers (N)", min_value=1, value=50, step=1)
    K = st.number_input("Winning numbers drawn (K)", min_value=1, max_value=N, value=5, step=1)
with col2:
    n = st.number_input("Your numbers (n)", min_value=1, max_value=N, value=10, step=1)
    k = st.number_input("Matches (k)", min_value=0, max_value=min(n, K), value=2, step=1)

# Validate inputs
if n > N:
    st.error("Your numbers (n) cannot exceed total numbers (N).")
elif K > N:
    st.error("Winning numbers (K) cannot exceed total numbers (N).")
elif k > min(n, K):
    st.error("Matches (k) cannot exceed the smaller of your numbers (n) or winning numbers (K).")
else:
    # Calculate probabilities
    # P(X = k): Probability of exactly k matches
    prob_exact = hypergeom.pmf(k, N, K, n)

    # P(X <= k): Cumulative probability of up to k matches
    prob_cumulative = hypergeom.cdf(k, N, K, n)

    # Display results
    st.subheader("Results")
    st.write(f"- **Probability of exactly {k} matches (P(X = {k}))**: {prob_exact:.6f} ({prob_exact * 100:.4f}%)")
    st.write(f"- **Probability of up to {k} matches (P(X <= {k}))**: {prob_cumulative:.6f} ({prob_cumulative * 100:.4f}%)")

    # Optional: Plot the probability mass function (PMF)
    if st.checkbox("Show probability distribution"):
        k_values = np.arange(0, min(n, K) + 1)
        pmf_values = [hypergeom.pmf(i, N, K, n) for i in k_values]
        st.line_chart(data={"k": k_values, "P(X = k)": pmf_values}, x="k", y="P(X = k)")
