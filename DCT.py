import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
from io import BytesIO

# Set page title and layout

st.set_page_config(page_title="DCT & Wavelet Transform Visualizer", layout="wide")

# Title

st.title("🖼️ DCT & Wavelet Transform Visualizer")
st.markdown("Upload an image to apply Discrete Cosine Transform (DCT) and visualize the results.")



# File uploader

uploaded_file = st.file_uploader(
    "Choose an image...",
    type=["jpg", "jpeg", "png", "bmp"],
    help="Upload an image file to process."
)

if uploaded_file is not None:
    # Load the image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)

if img is None:
    st.error("❌ Failed to read the image. Please upload a valid image file.")
else:
    st.success("✅ Image loaded successfully!")

    # Display original image
    st.subheader("Original Image (Grayscale)")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.imshow(img, cmap="gray")
    ax.axis("off")
    st.pyplot(fig)

    # Apply DCT
    def apply_dct(img):
        imf = np.float32(img) / 255.0
        dct_img = cv2.dct(imf)
        dct_disp = np.clip(dct_img, 0.0, 1.0)
        return (dct_disp * 255).astype(np.uint8)

    dct_out = apply_dct(img)

    # Display DCT transformed image
    st.subheader("DCT Transformed Image")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.imshow(dct_out, cmap="gray", vmin=0, vmax=255)
    ax.axis("off")
    st.pyplot(fig)

    # Optional: Wavelet Transform (uncomment if needed)
    # st.subheader("Wavelet Reconstructed Image")
    # try:
    #     import pywt
    #     def apply_wavelet(img):
    #         coeffs = pywt.wavedec2(img, 'haar', level=2)
    #         rec = pywt.waverec2(coeffs, 'haar')
    #         rec = np.clip(rec, 0, 255).astype(np.uint8)
    #         return rec
    #     wave_out = apply_wavelet(img)
    #     fig, ax = plt.subplots(figsize=(6, 4))
    #     ax.imshow(wave_out, cmap="gray")
    #     ax.axis("off")
    #     st.pyplot(fig)
    # except ImportError:
    #     st.warning("⚠️ PyWavelets (`pywt`) not installed. Install it with `uv add pywavelets`.")

    # Download buttons
    st.subheader("Download Results")
    col1, col2 = st.columns(2)

    with col1:
        # Save original image
        _, buffer = cv2.imencode('.png', img)
        st.download_button(
            label="📥 Download Original Image",
            data=buffer.tobytes(),
            file_name="original.png",
            mime="image/png"
        )

    with col2:
        # Save DCT image
        _, buffer = cv2.imencode('.png', dct_out)
        st.download_button(
            label="📥 Download DCT Image",
            data=buffer.tobytes(),
            file_name="dct_transformed.png",
            mime="image/png"
        )

# Footer

st.markdown("---")
st.markdown(
    """
    ### About
    This app applies the Discrete Cosine Transform (DCT) to an uploaded image.
    DCT is widely used in image compression (e.g., JPEG) and signal processing.

**Try it out!** Upload an image to see the transformation in action.
"""

)
