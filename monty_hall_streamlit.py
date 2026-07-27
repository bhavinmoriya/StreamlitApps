import streamlit as st
import random
import pandas as pd
import plotly.express as px

# Title and description
st.title("Monty Hall Problem Simulator")
st.write("""
This app simulates the Monty Hall problem for any number of doors.
Choose the number of doors and trials, then see how switching improves your odds!
""")

# Sidebar for user inputs
st.sidebar.header("Simulation Parameters")
num_doors = st.sidebar.slider("Number of doors", min_value=3, max_value=1000, value=3, step=1)
num_simulations = st.sidebar.slider("Number of simulations", min_value=100, max_value=100000, value=10000, step=1000)

# Function to run the simulation
def monty_hall_simulation(num_doors, num_simulations):
    stick_wins = 0
    switch_wins = 0

    for _ in range(num_simulations):
        car_behind = random.randint(0, num_doors - 1)
        contestant_choice = random.randint(0, num_doors - 1)

        # Host opens N-2 doors (all goats)
        remaining_doors = [door for door in range(num_doors) if door != contestant_choice and door != car_behind]
        host_opens = random.sample(remaining_doors, num_doors - 2)

        # Determine the door to switch to
        switch_to = [door for door in range(num_doors) if door != contestant_choice and door not in host_opens][0]

        if contestant_choice == car_behind:
            stick_wins += 1
        if switch_to == car_behind:
            switch_wins += 1

    return stick_wins, switch_wins

# Run the simulation
stick_wins, switch_wins = monty_hall_simulation(num_doors, num_simulations)

# Calculate win percentages
stick_win_percentage = (stick_wins / num_simulations) * 100
switch_win_percentage = (switch_wins / num_simulations) * 100

# Display results
st.subheader(f"Results for {num_doors} doors and {num_simulations} simulations")
results_df = pd.DataFrame({
    "Strategy": ["Stick with initial choice", "Switch to remaining door"],
    "Win Rate (%)": [stick_win_percentage, switch_win_percentage]
})

# Show table
st.table(results_df)

# Plot the results
fig = px.bar(
    results_df,
    x="Strategy",
    y="Win Rate (%)",
    title=f"Win Rate Comparison for {num_doors} Doors",
    color="Strategy",
    text="Win Rate (%)"
)
fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
st.plotly_chart(fig, use_container_width=True)

# Theoretical probabilities
st.subheader("Theoretical Probabilities")
theoretical_stick = 100 / num_doors
theoretical_switch = 100 * (num_doors - 1) / num_doors
st.write(f"- **Stick win probability**: {theoretical_stick:.2f}%")
st.write(f"- **Switch win probability**: {theoretical_switch:.2f}%")
