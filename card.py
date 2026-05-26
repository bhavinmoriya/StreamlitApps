import streamlit as st
import pandas as pd

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
    # st.write("Compare different cards and scenarios...")
    # Add comparison charts or additional calculations here
    st.header("📊 Card Comparison")
    
    # Define card options
    cards = [
        {"Name": "Card 1", "Spend": 9000, "Return %": 1.25, "Fees": 0},
        {"Name": "Card 2", "Spend": 10000, "Return %": 1.7, "Fees": 50},
        {"Name": "Card 3", "Spend": 12000, "Return %": 1.8, "Fees": 100}
    ]

    # Calculate benefits for each card
    results = []
    for card in cards:
        cashback, r = card_benefit(card["Spend"], card["Return %"], card["Fees"])
        results.append({
            "Card": card["Name"],
            "Spend (€)": card["Spend"],
            "Return %": card["Return %"],
            "Fees (€)": card["Fees"],
            "Cashback (€)": f"{cashback:.2f}",
            "Effective Return %": f"{r:.2f}"
        })

    # Display as DataFrame
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)

    # Highlight best card
    best_card = df.loc[df["Effective Return %"].astype(float).idxmax()]
    st.success(f"**Best Card: {best_card['Card']}** with **{best_card['Effective Return %']}%** effective return")
