import streamlit as st

def card_benefit(spend=9000, return_percentage=1.25, fees=0):
    cashback = spend * return_percentage / 100
    cashback = cashback - fees
    r = cashback * 100 / spend
    return cashback, r

# --- Streamlit App ---
st.set_page_config(page_title="Cashback Calculator", layout="wide")

tab1, tab2 = st.tabs(["Cashback Calculator", "Analysis"])

with tab1:
    st.header("💳 Card Cashback Calculator")
    spend = st.number_input("Spending Amount (€)", value=9000.0, step=100.0)
    return_percentage = st.number_input("Return Percentage (%)", value=1.25, step=0.25)
    fees = st.number_input("Annual Fees (€)", value=0.0, step=1.0)

    if st.button("Calculate"):
        cashback, r = card_benefit(spend, return_percentage, fees)
        st.success(f"**Cashback: €{cashback:.2f}** | **Effective Return: {r:.2f}%**")

with tab2:
    st.header("📊 Detailed Analysis")
    st.write("Compare different cards and scenarios...")
    # Add comparison charts or additional calculations here
