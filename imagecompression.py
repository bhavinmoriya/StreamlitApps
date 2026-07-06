import streamlit as st
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

st.title("Image Compression with SVD")

# --- Upload an image ---
uploaded_file = st.file_uploader("Upload an image:", type=["jpg", "png", "jpeg"])
if uploaded_file is None:
    st.stop()

# --- Convert to grayscale and resize ---
image = Image.open(uploaded_file).convert("L")  # Grayscale
image = image.resize((100, 100))  # Resize for faster computation
img_array = np.array(image, dtype=np.float32)

# --- Compute SVD ---
U, S, Vt = np.linalg.svd(img_array)

# --- Select number of singular values to keep ---
k = st.slider("Number of singular values to keep (k):", min_value=1, max_value=min(img_array.shape), value=10)

# --- Reconstruct image ---
S_k = np.diag(S[:k])
U_k = U[:, :k]
Vt_k = Vt[:k, :]
reconstructed = U_k @ S_k @ Vt_k

# --- Display results ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
ax1.imshow(img_array, cmap="gray")
ax1.set_title("Original Image")
ax1.axis("off")
ax2.imshow(reconstructed, cmap="gray")
ax2.set_title(f"Compressed (k={k})")
ax2.axis("off")
st.pyplot(fig)

# --- Compression ratio ---
original_size = img_array.size
compressed_size = (U_k.size + S_k.size + Vt_k.size)
ratio = original_size / compressed_size
st.write(f"**Compression ratio:** {ratio:.2f}x")

linkedin_url = "https://www.linkedin.com/in/bhavin-moriya-ph-d-b0b88b2/"
github_url = "https://github.com/bhavinmoriya"

st.markdown("## Connect with me")

col1, col2 = st.columns(2)

with col1:
    st.link_button("🔗 Follow on LinkedIn", linkedin_url)

with col2:
    st.link_button("💻 Follow on GitHub", github_url)
