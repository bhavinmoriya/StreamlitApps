import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Title and description
st.title("Logistic Map Simulation")
st.write("""
This app simulates the logistic map equation: **xₙ₊₁ = r * xₙ * (1 - xₙ)**.
Adjust the growth rate *r* and initial population *x₀* to see how the system evolves.
""")

# User inputs
r = st.slider("Growth Rate (r)", 0.0, 4.0, 2.5, 0.01)
x0 = st.slider("Initial Population (x₀)", 0.0, 1.0, 0.5, 0.01)
n_iterations = st.slider("Number of Iterations", 10, 1000, 100, 10)

# Simulate the logistic map
def logistic_map(r, x0, n):
    x = np.zeros(n)
    x[0] = x0
    for i in range(1, n):
        x[i] = r * x[i-1] * (1 - x[i-1])
    return x

x_values = logistic_map(r, x0, n_iterations)

# Plot the results
fig, ax = plt.subplots()
ax.plot(x_values, marker='o', linestyle='-', markersize=2)
ax.set_title(f"Logistic Map (r = {r}, x₀ = {x0})")
ax.set_xlabel("Iteration")
ax.set_ylabel("Population (xₙ)")
ax.grid(True)

st.pyplot(fig)

# Show the final value
st.write(f"Final population value: **{x_values[-1]:.4f}**")
