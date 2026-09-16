import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Function to plot vectors and transformations
def plot_svd_transformations(A, x, rank):
    # Compute SVD
    U, s, VT = np.linalg.svd(A)
    Sigma = np.diag(s)

    # Rank-1 approximation: Keep only the largest singular value
    if rank == 1:
        Sigma_rank = np.diag([s[0], 0])
    else:
        Sigma_rank = Sigma

    # Construct V from VT
    V = VT.T

    # Apply transformations step-by-step
    x_VT = VT @ x
    x_Sigma_VT = Sigma_rank @ x_VT
    x_U_Sigma_VT = U @ x_Sigma_VT

    # Create a figure
    fig, axs = plt.subplots(1, 4, figsize=(16, 4))

    # Plot original vector
    axs[0].quiver(0, 0, x[0], x[1], angles='xy', scale_units='xy', scale=1, color='red')
    axs[0].set_xlim(-2, 2)
    axs[0].set_ylim(-2, 2)
    axs[0].set_title("Original Vector")
    axs[0].grid()

    # Plot after V^T (rotation/reflection)
    axs[1].quiver(0, 0, x_VT[0], x_VT[1], angles='xy', scale_units='xy', scale=1, color='blue')
    axs[1].set_xlim(-2, 2)
    axs[1].set_ylim(-2, 2)
    axs[1].set_title("After $V^T$ (Rotation)")
    axs[1].grid()

    # Plot after Sigma (stretching)
    axs[2].quiver(0, 0, x_Sigma_VT[0], x_Sigma_VT[1], angles='xy', scale_units='xy', scale=1, color='green')
    axs[2].set_xlim(-2, 2)
    axs[2].set_ylim(-2, 2)
    axs[2].set_title(f"After $\\Sigma$ (Stretching, Rank-{rank})")
    axs[2].grid()

    # Plot after U (rotation/reflection)
    axs[3].quiver(0, 0, x_U_Sigma_VT[0], x_U_Sigma_VT[1], angles='xy', scale_units='xy', scale=1, color='purple')
    axs[3].set_xlim(-2, 2)
    axs[3].set_ylim(-2, 2)
    axs[3].set_title("After $U$ (Rotation)")
    axs[3].grid()

    plt.tight_layout()
    return fig

# Streamlit app
st.title("SVD Transformation Visualization with Rank Approximation")
st.write("This app visualizes the SVD decomposition of a 2x2 matrix as a sequence of rotations and stretching, with rank-1 or rank-2 approximation.")

# Input for the matrix A
st.subheader("Input Matrix A (2x2)")
a11 = st.number_input("A[0,0]", value=1.0)
a12 = st.number_input("A[0,1]", value=0.0)
a21 = st.number_input("A[1,0]", value=0.0)
a22 = st.number_input("A[1,1]", value=1.0)

A = np.array([[a11, a12], [a21, a22]])

# Input for the vector x
st.subheader("Input Vector x (2D)")
x1 = st.number_input("x[0]", value=1.0)
x2 = st.number_input("x[1]", value=0.0)

x = np.array([x1, x2])

# Select rank approximation
st.subheader("Select Rank Approximation")
rank = st.radio("Rank:", options=[1, 2], index=1)

# Compute and plot SVD transformations
if st.button("Visualize SVD Transformations"):
    fig = plot_svd_transformations(A, x, rank)
    st.pyplot(fig)

    # Display SVD components
    U, s, VT = np.linalg.svd(A)
    st.subheader("SVD Components")
    st.write(f"$U$ (Rotation Matrix):\n {U}")
    st.write(f"$\\Sigma$ (Stretching Matrix):\n {np.diag(s)}")
    st.write(f"$V^T$ (Rotation Matrix):\n {VT}")

    # Display rank-approximated matrix
    if rank == 1:
        A_rank1 = U @ np.diag([s[0], 0]) @ VT
        st.subheader("Rank-1 Approximation of A")
        st.write(A_rank1)
    else:
        st.subheader("Full Rank (Rank-2) Approximation of A")
        st.write(A)
