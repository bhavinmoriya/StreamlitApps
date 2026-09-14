import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Title
st.title("Vector Rotation App")

# Input: Dimension
dimension = st.selectbox("Select Dimension:", [1, 2])

# Input: Vector
if dimension == 1:
    x = st.number_input("Enter the vector component (x):", value=1.0)
    vector = np.array([x])
else:
    x = st.number_input("Enter x-component:", value=1.0)
    y = st.number_input("Enter y-component:", value=0.0)
    vector = np.array([x, y])

# Input: Rotation angle (degrees)
theta_deg = st.number_input("Enter rotation angle (degrees):", value=45.0)
theta_rad = np.radians(theta_deg)

# Rotation matrix for 2D
if dimension == 2:
    rotation_matrix = np.array([
        [np.cos(theta_rad), -np.sin(theta_rad)],
        [np.sin(theta_rad), np.cos(theta_rad)]
    ])
    rotated_vector = rotation_matrix @ vector
else:
    # For 1D, rotation is trivial (no change)
    rotated_vector = vector

# Plot
fig, ax = plt.subplots(figsize=(6, 6))

if dimension == 1:
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.axvline(0, color="black", linewidth=0.5)
    ax.quiver(0, 0, vector[0], 0, angles="xy", scale_units="xy", scale=1, color="blue", label="Original Vector")
    ax.quiver(0, 0, rotated_vector[0], 0, angles="xy", scale_units="xy", scale=1, color="red", label="Rotated Vector")
else:
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.axvline(0, color="black", linewidth=0.5)
    ax.quiver(0, 0, vector[0], vector[1], angles="xy", scale_units="xy", scale=1, color="blue", label="Original Vector")
    ax.quiver(0, 0, rotated_vector[0], rotated_vector[1], angles="xy", scale_units="xy", scale=1, color="red", label="Rotated Vector")

ax.set_aspect("equal")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Output: Rotated vector
st.subheader("Rotated Vector:")
st.write(rotated_vector)
