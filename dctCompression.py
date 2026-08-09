import streamlit as st
import numpy as np
import matplotlib
matplotlib.use("Agg")  # important for non-GUI backends on cloud
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.fftpack import dct, idct

st.set_page_config(layout="wide")

# Title
st.title("DCT for Audio Compression")

# Upload a WAV file
st.subheader("Upload an audio file (WAV format)")
audio_file = st.file_uploader("Audio File", type=["wav"], key="audio_uploader")

if audio_file is not None:
    # Read the WAV file
    sample_rate, signal = wavfile.read(audio_file)
    if len(signal.shape) > 1:
        signal = signal[:, 0]  # Convert to mono
    signal = signal.astype(float) / np.max(np.abs(signal))  # Normalize to float

    # Apply DCT (cached implicitly by being deterministic per file+run)
    dct_coeffs = dct(signal)

    # ---- Original signal and DCT coefficients ----
    st.subheader("Original Signal and DCT Coefficients")

    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
    ax1.plot(signal, label="Original Signal", color="blue")
    ax1.set_title("Original Audio Signal")
    ax1.set_xlabel("Samples")
    ax1.set_ylabel("Amplitude")
    ax1.grid(True)
    ax1.legend()

    ax2.plot(np.abs(dct_coeffs), label="DCT Coefficients", color="red")
    ax2.set_title("Magnitude of DCT Coefficients")
    ax2.set_xlabel("Coefficient Index")
    ax2.set_ylabel("Magnitude")
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    st.pyplot(fig1, use_container_width=True, key="plot_original_dct")
    plt.close(fig1)

    # ---- Compression demo ----
    st.subheader("Compression Demo")

    num_coeffs = st.slider(
        "Number of DCT coefficients to keep (for reconstruction):",
        min_value=1,
        max_value=len(dct_coeffs),
        value=max(1, len(dct_coeffs) // 2),
        step=1,
        key="num_coeffs_slider",  # stable key
    )

    # Reconstruct signal using top N coefficients
    reconstructed_coeffs = np.zeros_like(dct_coeffs)
    reconstructed_coeffs[:num_coeffs] = dct_coeffs[:num_coeffs]
    reconstructed_signal = idct(reconstructed_coeffs)

    # Normalize reconstructed signal safely
    max_abs = np.max(np.abs(reconstructed_signal))
    if max_abs > 0:
        reconstructed_signal = reconstructed_signal / max_abs

    # ---- Reconstructed signal and error ----
    fig2, (ax3, ax4) = plt.subplots(2, 1, figsize=(10, 6))

    ax3.plot(signal, label="Original Signal", color="blue", alpha=0.5)
    ax3.plot(reconstructed_signal, label="Reconstructed Signal", color="green")
    ax3.set_title(f"Reconstructed Signal (Top {num_coeffs} DCT Coefficients)")
    ax3.set_xlabel("Samples")
    ax3.set_ylabel("Amplitude")
    ax3.legend()
    ax3.grid(True)

    # Plot error
    error = signal - reconstructed_signal
    ax4.plot(error, label="Error", color="red")
    ax4.set_title("Error (Original - Reconstructed)")
    ax4.set_xlabel("Samples")
    ax4.set_ylabel("Amplitude")
    ax4.legend()
    ax4.grid(True)

    plt.tight_layout()
    st.pyplot(fig2, use_container_width=True, key="plot_reconstruction_error")
    plt.close(fig2)

    # Calculate compression ratio
    original_size = len(signal)
    compressed_size = num_coeffs
    compression_ratio = (original_size - compressed_size) / original_size * 100
    st.write(
        f"**Compression Ratio:** {compression_ratio:.2f}% "
        f"(Kept {num_coeffs}/{original_size} coefficients)"
    )

    # Play original and reconstructed audio
    st.subheader("Listen to the Difference")
    st.audio(signal, sample_rate=sample_rate, format="audio/wav", key="audio_original")
    st.audio(
        reconstructed_signal,
        sample_rate=sample_rate,
        format="audio/wav",
        key="audio_reconstructed",
    )
