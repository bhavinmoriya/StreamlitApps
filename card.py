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
    st.header("📊 Compare Multiple Cards")

    # Select number of cards
    num_cards = st.number_input(
        "Number of cards to compare",
        min_value=1,
        max_value=10,
        value=2,
        step=1
    )

    # Input fields for each card
    cards = []
    for i in range(num_cards):
        with st.expander(f"Card {i+1}", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                spend = st.number_input(
                    "Spend (€)",
                    key=f"spend_{i}",
                    value=9000.0,
                    step=100.0
                )
            with col2:
                return_pct = st.number_input(
                    "Return %",
                    key=f"return_{i}",
                    value=1.25,
                    step=0.25
                )
            with col3:
                fees = st.number_input(
                    "Fees (€)",
                    key=f"fees_{i}",
                    value=0.0,
                    step=1.0
                )
            cards.append((spend, return_pct, fees))

    if st.button("Compare All Cards"):
        results = []
        for i, (spend, return_pct, fees) in enumerate(cards):
            cashback, r = card_benefit(spend, return_pct, fees)
            results.append({
                "Card": f"Card {i+1}",
                "Spend (€)": spend,
                "Return %": return_pct,
                "Fees (€)": fees,
                "Cashback (€)": f"{cashback:.2f}",
                "Effective Return %": f"{r:.2f}"
            })

        # Display results
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)

        # Highlight best card
        if not df.empty:
            best_idx = df["Effective Return %"].astype(float).idxmax()
            best_card = df.loc[best_idx]
            st.success(f"**🏆 Best Card: {best_card['Card']}** with **{best_card['Effective Return %']}%** effective return")
