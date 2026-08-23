import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve
from scipy.io import wavfile

# Set style for plots
plt.style.use("ggplot")

# Title
st.title("Audio Signal Convolution")

# Upload two audio files (WAV format)
st.subheader("Upload two audio signals (WAV files)")
file1 = st.file_uploader("Signal 1", type=["wav"])
file2 = st.file_uploader("Signal 2", type=["wav"])

if file1 and file2:
    # Read WAV files
    sample_rate1, signal1 = wavfile.read(file1)
    sample_rate2, signal2 = wavfile.read(file2)

    # Ensure signals are mono (take first channel if stereo)
    if len(signal1.shape) > 1:
        signal1 = signal1[:, 0]
    if len(signal2.shape) > 1:
        signal2 = signal2[:, 0]

    # Normalize signals to [-1, 1]
    signal1 = signal1.astype(float) / np.max(np.abs(signal1))
    signal2 = signal2.astype(float) / np.max(np.abs(signal2))

    # Compute convolution
    convolved_signal = convolve(signal1, signal2, mode="full")

    # Normalize convolved signal for visualization
    convolved_signal = convolved_signal / np.max(np.abs(convolved_signal))

    # Plot the signals
    st.subheader("Input Signals and Convolution Result")

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))

    # Plot Signal 1
    ax1.plot(signal1, label="Signal 1", color="blue")
    ax1.set_title("Signal 1")
    ax1.set_xlabel("Samples")
    ax1.set_ylabel("Amplitude")
    ax1.grid(True)

    # Plot Signal 2
    ax2.plot(signal2, label="Signal 2", color="orange")
    ax2.set_title("Signal 2")
    ax2.set_xlabel("Samples")
    ax2.set_ylabel("Amplitude")
    ax2.grid(True)

    # Plot Convolved Signal
    ax3.plot(convolved_signal, label="Convolved Signal", color="green")
    ax3.set_title("Convolution Result")
    ax3.set_xlabel("Samples")
    ax3.set_ylabel("Amplitude")
    ax3.grid(True)

    plt.tight_layout()
    st.pyplot(fig)

    # Option to download the convolved signal as WAV
    st.subheader("Download Convolved Signal")
    if st.button("Generate WAV File"):
        # Scale to 16-bit PCM range
        convolved_signal_int16 = np.int16(convolved_signal * 32767)
        wavfile.write("convolved_signal.wav", sample_rate1, convolved_signal_int16)
        st.success("Convolved signal saved as WAV!")
        st.audio("convolved_signal.wav", format="audio/wav")
else:
    st.info("Please upload two WAV files to compute their convolution.")

linkedin_url = "https://www.linkedin.com/in/bhavin-moriya-ph-d-b0b88b2/"
github_url = "https://github.com/bhavinmoriya"
youtube_url = "https://www.youtube.com/@bhavinmoriya9216"
st.markdown("## Connect with me")

col1, col2, col3 = st.columns(3)

with col1:
    st.link_button("🔗 Follow on LinkedIn", linkedin_url)

with col2:
    st.link_button("💻 Follow on GitHub", github_url)

with col3:
    st.link_button("🔗 Subscribe on YouTube", youtube_url)
