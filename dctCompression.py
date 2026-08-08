import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.fftpack import dct, idct

# Title
st.title("DCT for Audio Compression")

# Upload a WAV file
st.subheader("Upload an audio file (WAV format)")
audio_file = st.file_uploader("Audio File", type=["wav"])

if audio_file:
    # Read the WAV file
    sample_rate, signal = wavfile.read(audio_file)
    if len(signal.shape) > 1:
        signal = signal[:, 0]  # Convert to mono
    signal = signal.astype(float) / np.max(np.abs(signal))  # Normalize

    # Apply DCT
    dct_coeffs = dct(signal)

    # Plot original signal and DCT coefficients
    st.subheader("Original Signal and DCT Coefficients")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
    ax1.plot(signal, label="Original Signal", color="blue")
    ax1.set_title("Original Audio Signal")
    ax1.set_xlabel("Samples")
    ax1.set_ylabel("Amplitude")
    ax1.grid(True)

    ax2.plot(np.abs(dct_coeffs), label="DCT Coefficients", color="red")
    ax2.set_title("Magnitude of DCT Coefficients")
    ax2.set_xlabel("Coefficient Index")
    ax2.set_ylabel("Magnitude")
    ax2.grid(True)
    st.pyplot(fig)

    # Compression: Reconstruct with top N coefficients
    st.subheader("Compression Demo")
    num_coeffs = st.slider(
        "Number of DCT coefficients to keep (for reconstruction):",
        min_value=1,
        max_value=len(dct_coeffs),
        value=len(dct_coeffs) // 2,
        step=1
    )

    # Reconstruct signal using top N coefficients
    reconstructed_coeffs = np.zeros_like(dct_coeffs)
    reconstructed_coeffs[:num_coeffs] = dct_coeffs[:num_coeffs]
    reconstructed_signal = idct(reconstructed_coeffs)

    # Normalize reconstructed signal
    reconstructed_signal = reconstructed_signal / np.max(np.abs(reconstructed_signal))

    # Plot reconstructed signal
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
    ax4.grid(True)
    st.pyplot(fig2)

    # Calculate compression ratio
    original_size = len(signal)
    compressed_size = num_coeffs
    compression_ratio = (original_size - compressed_size) / original_size * 100
    st.write(f"**Compression Ratio:** {compression_ratio:.2f}% (Kept {num_coeffs}/{original_size} coefficients)")

    # Play original and reconstructed audio
    st.subheader("Listen to the Difference")
    st.audio(signal, sample_rate=sample_rate, format="audio/wav")
    st.audio(reconstructed_signal, sample_rate=sample_rate, format="audio/wav")
else:
    st.info("Please upload a WAV file to see DCT in action.")
