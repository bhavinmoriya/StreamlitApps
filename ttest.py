import streamlit as st
from scipy import stats
import numpy as np

st.title("T-Test App")

test_type = st.selectbox("Choose test type", ["One-sample t-test", "Two-sample t-test"])

def parse_numbers(text):
    return np.array([float(x) for x in text.split(",") if x.strip()])

if test_type == "One-sample t-test":
    data_text = st.text_input("Enter sample data (comma-separated)")
    mu0 = st.number_input("Hypothesized mean", value=0.0)

    if st.button("Run test"):
        data = parse_numbers(data_text)
        t_stat, p_value = stats.ttest_1samp(data, mu0)
        st.write("t-statistic:", t_stat)
        st.write("p-value:", p_value)

else:
    data1_text = st.text_input("Enter group 1 data (comma-separated)")
    data2_text = st.text_input("Enter group 2 data (comma-separated)")
    equal_var = st.checkbox("Assume equal variances", value=False)

    if st.button("Run test"):
        data1 = parse_numbers(data1_text)
        data2 = parse_numbers(data2_text)
        t_stat, p_value = stats.ttest_ind(data1, data2, equal_var=equal_var)
        st.write("t-statistic:", t_stat)
        st.write("p-value:", p_value)
