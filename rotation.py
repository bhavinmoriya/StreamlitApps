import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Title
st.title("Vector Rotation App (1D, 2D, 3D)")

# Input: Dimension
dimension = st.selectbox("Select Dimension:", [1, 2, 3])

# Input: Vector
if dimension == 1:
    x = st.number_input("Enter the vector component (x):", value=1.0)
    vector = np.array([x])
elif dimension == 2:
    x = st.number_input("Enter x-component:", value=1.0)
    y = st.number_input("Enter y-component:", value=0.0)
    vector = np.array([x, y])
else:  # 3D
    x = st.number_input("Enter x-component:", value=1.0)
    y = st.number_input("Enter y-component:", value=0.0)
    z = st.number_input("Enter z-component:", value=0.0)
    vector = np.array([x, y, z])

# Input: Rotation angle (degrees)
theta_deg = st.number_input("Enter rotation angle (degrees):", value=45.0)
theta_rad = np.radians(theta_deg)

# Rotation matrix
if dimension == 1:
    # No rotation in 1D
    rotated_vector = vector
elif dimension == 2:
    rotation_matrix = np.array([
        [np.cos(theta_rad), -np.sin(theta_rad)],
        [np.sin(theta_rad), np.cos(theta_rad)]
    ])
    rotated_vector = rotation_matrix @ vector
else:  # 3D
    axis = st.selectbox("Select rotation axis:", ["X", "Y", "Z"])
    if axis == "X":
        rotation_matrix = np.array([
            [1, 0, 0],
            [0, np.cos(theta_rad), -np.sin(theta_rad)],
            [0, np.sin(theta_rad), np.cos(theta_rad)]
        ])
    elif axis == "Y":
        rotation_matrix = np.array([
            [np.cos(theta_rad), 0, np.sin(theta_rad)],
            [0, 1, 0],
            [-np.sin(theta_rad), 0, np.cos(theta_rad)]
        ])
    else:  # Z
        rotation_matrix = np.array([
            [np.cos(theta_rad), -np.sin(theta_rad), 0],
            [np.sin(theta_rad), np.cos(theta_rad), 0],
            [0, 0, 1]
        ])
    rotated_vector = rotation_matrix @ vector

# Plot
fig = plt.figure(figsize=(8, 6))

if dimension == 1:
    ax = fig.add_subplot(111)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.axvline(0, color="black", linewidth=0.5)
    ax.quiver(0, 0, vector[0], 0, angles="xy", scale_units="xy", scale=1, color="blue", label="Original Vector")
    ax.quiver(0, 0, rotated_vector[0], 0, angles="xy", scale_units="xy", scale=1, color="red", label="Rotated Vector")
elif dimension == 2:
    ax = fig.add_subplot(111)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.axvline(0, color="black", linewidth=0.5)
    ax.quiver(0, 0, vector[0], vector[1], angles="xy", scale_units="xy", scale=1, color="blue", label="Original Vector")
    ax.quiver(0, 0, rotated_vector[0], rotated_vector[1], angles="xy", scale_units="xy", scale=1, color="red", label="Rotated Vector")
else:  # 3D
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_zlim(-2, 2)
    ax.quiver(0, 0, 0, vector[0], vector[1], vector[2], color="blue", label="Original Vector")
    ax.quiver(0, 0, 0, rotated_vector[0], rotated_vector[1], rotated_vector[2], color="red", label="Rotated Vector")

ax.set_aspect("equal")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Output: Rotated vector
st.subheader("Rotated Vector:")
st.write(rotated_vector)
