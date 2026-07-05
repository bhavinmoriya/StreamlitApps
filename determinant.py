import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

# Function to calculate determinant with cofactor expansion
def determinant(matrix):
    # Base case for 1x1 matrix
    if matrix.shape == (1, 1):
        return matrix[0, 0]
    # Base case for 2x2 matrix
    if matrix.shape == (2, 2):
        return matrix[0, 0] * matrix[1, 1] - matrix[0, 1] * matrix[1, 0]
    det = 0
    for col in range(matrix.shape[1]):
        minor = matrix[1:, :col].copy()  # Create minor matrix
        minor = np.append(minor, matrix[1:, col+1:], axis=1)
        sign = (-1) ** col
        det += sign * matrix[0, col] * determinant(minor)
    return det

# Animation function (simplified)
def animate_determinant(matrix, steps):
    fig, ax = plt.subplots()
    ax.matshow(matrix, cmap='viridis')
    ax.set_title("Calculating Determinant...")

    def update(frame):
        ax.clear()
        ax.matshow(matrix, cmap='viridis')
        ax.set_title(f"Step {frame + 1}: Expanding along row 0")
        # Add annotations, highlights, etc.
        return ax

    ani = FuncAnimation(fig, update, frames=len(steps), interval=1000)
    return ani

# Streamlit app
st.title("Interactive Determinant Calculator")
n = st.slider("Matrix size", 2, 5, 3)
matrix = np.random.randint(-5, 5, (n, n))  # Random matrix for demo
st.write("Matrix:", matrix)

if st.button("Calculate Determinant"):
    det = determinant(matrix)
    st.write("Determinant:", det)
    # Display animation (simplified for Streamlit)
    st.pyplot(animate_determinant(matrix, range(n)))
