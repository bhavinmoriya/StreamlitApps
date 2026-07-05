import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Function to calculate determinant with cofactor expansion
def determinant(matrix):
    if matrix.shape == (1, 1):
        return matrix[0, 0]
    if matrix.shape == (2, 2):
        return matrix[0, 0] * matrix[1, 1] - matrix[0, 1] * matrix[1, 0]
    det = 0
    for col in range(matrix.shape[1]):
        minor = np.delete(np.delete(matrix, 0, axis=0), col, axis=1)
        sign = (-1) ** col
        det += sign * matrix[0, col] * determinant(minor)
    return det

# Function to generate animation frames for cofactor expansion
def generate_animation_frames(matrix):
    frames = []
    n = matrix.shape[0]
    for col in range(n):
        # Create a copy of the matrix for this frame
        frame_matrix = matrix.copy()
        # Highlight the current column
        frame_matrix[:, col] = 10  # Arbitrary high value for visualization
        frames.append(frame_matrix)
    return frames

# Function to create Plotly figure for a matrix
def create_matrix_fig(matrix, title):
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        colorscale='Viridis',
        text=np.round(matrix, 2),
        texttemplate='%{text}',
        textfont={"size": 20},
        colorbar=dict(title="Value")
    ))
    fig.update_layout(
        title=title,
        xaxis=dict(tickmode='linear', tick0=0.5, dtick=1, showticklabels=False),
        yaxis=dict(tickmode='linear', tick0=0.5, dtick=1, showticklabels=False),
        height=400,
        width=400
    )
    return fig

# Function to create animation
def create_animation(matrix):
    frames = generate_animation_frames(matrix)
    fig = create_matrix_fig(matrix, "Original Matrix")

    # Create a list of frames for the animation
    animation_frames = []
    for i, frame_matrix in enumerate(frames):
        animation_frames.append(
            go.Frame(
                data=[go.Heatmap(z=frame_matrix)],
                name=f"Step {i+1}"
            )
        )

    # Add frames to the figure
    fig.frames = animation_frames

    # Add buttons to control animation
    fig.update_layout(
        updatemenus=[{
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 500, "redraw": True},
                                   "fromcurrent": True, "transition": {"duration": 0}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                       "mode": "immediate",
                                       "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }]
    )
    return fig

# Streamlit app
st.title("Interactive Determinant Calculator with Animation")
st.write("Adjust the sliders to change the matrix values.")

# Initialize matrix
n = 3
matrix = np.zeros((n, n))

# Create sliders for matrix input
for i in range(n):
    cols = st.columns(n)
    for j in range(n):
        matrix[i, j] = cols[j].slider(
            f"Matrix[{i}][{j}]",
            -10.0, 10.0, 0.0, 0.1,
            key=f"matrix_{i}_{j}"
        )

# Display the matrix
st.subheader("Matrix")
st.write(matrix)

# Calculate and display determinant
det = determinant(matrix)
st.subheader("Determinant")
st.write(f"**Determinant = {det:.2f}**")

# Animate the cofactor expansion
st.subheader("Cofactor Expansion Animation")
if st.button("Animate"):
    anim_fig = create_animation(matrix)
    st.plotly_chart(anim_fig)
