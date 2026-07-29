import io

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from scipy.io import wavfile


st.set_page_config(
    page_title="Fourier Voice Lab",
    page_icon="🎙️",
    layout="wide",
)


# ---------------------------------------------------------
# Audio utilities
# ---------------------------------------------------------

def read_audio(audio_file):
    """Read WAV bytes and return sample rate + mono float signal."""

    sample_rate, signal = wavfile.read(io.BytesIO(audio_file.getvalue()))

    # Convert stereo -> mono
    if signal.ndim == 2:
        signal = signal.mean(axis=1)

    # Convert integer PCM -> floating point
    if np.issubdtype(signal.dtype, np.integer):
        info = np.iinfo(signal.dtype)
        scale = max(abs(info.min), info.max)
        signal = signal.astype(np.float64) / scale
    else:
        signal = signal.astype(np.float64)

    # Remove DC offset
    signal -= signal.mean()

    # Normalize
    max_value = np.max(np.abs(signal))
    if max_value > 0:
        signal /= max_value

    return sample_rate, signal


def compute_fft(signal, sample_rate):
    """Compute one-sided FFT."""

    n = len(signal)

    # Windowing reduces spectral leakage
    window = np.hanning(n)
    windowed = signal * window

    spectrum = np.fft.rfft(windowed)
    frequencies = np.fft.rfftfreq(n, d=1 / sample_rate)

    amplitudes = np.abs(spectrum)

    return frequencies, spectrum, amplitudes


def reconstruct_from_components(
    frequencies,
    spectrum,
    selected_indices,
    n_samples,
    sample_rate,
):
    """Reconstruct signal from selected positive-frequency components."""

    t = np.arange(n_samples) / sample_rate

    reconstructed = np.zeros(n_samples)

    # DC component
    if 0 in selected_indices:
        reconstructed += spectrum[0].real / n_samples

    for k in selected_indices:
        if k == 0:
            continue

        amplitude = 2 * np.abs(spectrum[k]) / n_samples
        phase = np.angle(spectrum[k])

        reconstructed += (
            amplitude
            * np.cos(2 * np.pi * frequencies[k] * t + phase)
        )

    # Normalize for playback
    max_value = np.max(np.abs(reconstructed))

    if max_value > 0:
        reconstructed /= max_value

    return reconstructed


def make_wav_bytes(signal, sample_rate):
    """Convert floating-point signal into WAV bytes."""

    signal = np.clip(signal, -1, 1)

    pcm = (signal * 32767).astype(np.int16)

    buffer = io.BytesIO()

    wavfile.write(
        buffer,
        sample_rate,
        pcm,
    )

    return buffer.getvalue()


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------

st.title("🎙️ Fourier Voice Lab")

st.markdown(
    """
Record your voice and explore how Fourier components build
the sound you hear.
"""
)

st.info(
    """
The experiment is:

**voice → waveform → Fourier transform → selected frequencies
→ inverse reconstruction → sound**
"""
)


# ---------------------------------------------------------
# Input
# ---------------------------------------------------------

audio = st.audio_input(
    "🎙️ Record your voice",
    sample_rate=16000,
)

uploaded = st.file_uploader(
    "Or upload a WAV file",
    type=["wav"],
)

audio_source = audio or uploaded


if audio_source is None:

    st.markdown(
        """
### Try saying something

For example:

> "The Fourier transform decomposes a signal into frequencies."

Then listen to what happens when we keep only a handful of
those frequencies.
"""
    )

    st.stop()


# ---------------------------------------------------------
# Read audio
# ---------------------------------------------------------

sample_rate, signal = read_audio(audio_source)


st.subheader("Original recording")

st.audio(audio_source)


duration = len(signal) / sample_rate

st.write(
    f"Sampling rate: **{sample_rate:,} Hz**  \n"
    f"Samples: **{len(signal):,}**  \n"
    f"Duration: **{duration:.2f} s**"
)


# ---------------------------------------------------------
# Waveform
# ---------------------------------------------------------

st.subheader("1. Time-domain waveform")

time = np.arange(len(signal)) / sample_rate

fig, ax = plt.subplots(figsize=(12, 3))

ax.plot(time, signal)

ax.set_xlabel("Time (seconds)")
ax.set_ylabel("Amplitude")
ax.set_title("Voice waveform")

ax.grid(alpha=0.25)

st.pyplot(fig)


# ---------------------------------------------------------
# FFT
# ---------------------------------------------------------

frequencies, spectrum, amplitudes = compute_fft(
    signal,
    sample_rate,
)


# Don't show extremely high frequencies for speech
max_frequency = min(8000, sample_rate / 2)

mask = frequencies <= max_frequency


st.subheader("2. Fourier spectrum")

fig, ax = plt.subplots(figsize=(12, 4))

ax.plot(
    frequencies[mask],
    amplitudes[mask],
)

ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("|X(f)|")
ax.set_title("Magnitude spectrum")

ax.grid(alpha=0.25)

st.pyplot(fig)


# ---------------------------------------------------------
# Find strongest components
# ---------------------------------------------------------

# Ignore DC component when finding dominant frequencies
search_amplitudes = amplitudes.copy()
search_amplitudes[0] = 0

num_components = st.slider(
    "Number of Fourier components",
    min_value=1,
    max_value=100,
    value=10,
)


strongest_indices = np.argsort(
    search_amplitudes
)[-num_components:][::-1]


st.subheader(
    f"3. Strongest {num_components} Fourier components"
)


component_data = []

for rank, k in enumerate(strongest_indices, start=1):

    component_data.append(
        {
            "Rank": rank,
            "Frequency (Hz)": round(float(frequencies[k]), 2),
            "Amplitude": round(float(amplitudes[k]), 4),
            "Phase (rad)": round(
                float(np.angle(spectrum[k])),
                4,
            ),
        }
    )


st.dataframe(
    component_data,
    width="stretch",
    hide_index=True,
)


# ---------------------------------------------------------
# Reconstruction
# ---------------------------------------------------------

st.subheader("4. Reconstruct the voice")


selected_indices = strongest_indices


reconstructed = reconstruct_from_components(
    frequencies=frequencies,
    spectrum=spectrum,
    selected_indices=selected_indices,
    n_samples=len(signal),
    sample_rate=sample_rate,
)


wav_bytes = make_wav_bytes(
    reconstructed,
    sample_rate,
)


st.audio(
    wav_bytes,
    format="audio/wav",
)


# ---------------------------------------------------------
# Compare original vs reconstruction
# ---------------------------------------------------------

st.subheader("5. Reconstruction")

fig, ax = plt.subplots(figsize=(12, 4))

# Only plot first 0.1 seconds so individual oscillations
# are visible.

plot_duration = min(0.1, duration)

n_plot = int(plot_duration * sample_rate)

ax.plot(
    time[:n_plot],
    signal[:n_plot],
    label="Original",
)

ax.plot(
    time[:n_plot],
    reconstructed[:n_plot],
    label="Reconstructed",
)

ax.set_xlabel("Time (seconds)")
ax.set_ylabel("Amplitude")

ax.legend()
ax.grid(alpha=0.25)

st.pyplot(fig)


# ---------------------------------------------------------
# Error
# ---------------------------------------------------------

mse = np.mean(
    (signal - reconstructed) ** 2
)

correlation = np.corrcoef(
    signal,
    reconstructed,
)[0, 1]


col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Mean squared error",
        f"{mse:.6f}",
    )

with col2:
    st.metric(
        "Correlation",
        f"{correlation:.4f}",
    )


# ---------------------------------------------------------
# Explanation
# ---------------------------------------------------------

with st.expander("🧠 What's happening mathematically?"):

    st.markdown(
        r"""
        For a sampled voice signal:
    
        $$
        x_0, x_1, \ldots, x_{N-1},
        $$
    
        the **Discrete Fourier Transform (DFT)** is:
    
        $$
        X_k = \sum_{n=0}^{N-1} x_n e^{-2\pi i kn/N}.
        $$
    
        Every \(X_k\) contains three pieces of information:
    
        $$
        X_k = |X_k|e^{i\phi_k}.
        $$
    
        So:
        - \(|X_k|\) = amplitude,
        - \(\phi_k\) = phase,
        - \(f_k = k f_s / N\) = frequency.
    
        ---
        The original signal can be reconstructed using:
    
        $$
        x_n = \frac{1}{N} \sum_{k=0}^{N-1} X_k e^{2\pi i kn/N}.
        $$
    
        The app deliberately throws away most of the \(X_k\)'s and keeps only the strongest components.
    
        Therefore, you are hearing approximately:
    
        $$
        \hat{x}(t) = \sum_{k \in S} A_k \cos(2\pi f_k t + \phi_k).
        $$
    
        ---
        **Experiment**: Increase the number of components:
    
        $$
        5 \rightarrow 10 \rightarrow 20 \rightarrow 50
        $$
    
        and listen to how the speech becomes progressively more recognizable.
        """
    )
#     st.markdown(
#         r"""
# For a sampled voice signal
# 
# \[
# x_0,x_1,\ldots,x_{N-1},
# \]
# 
# the discrete Fourier transform is
# 
# \[
# X_k =
# \sum_{n=0}^{N-1}
# x_n e^{-2\pi i kn/N}.
# \]
# 
# Every \(X_k\) contains three pieces of information:
# 
# \[
# X_k = |X_k|e^{i\phi_k}.
# \]
# 
# So:
# 
# - \(|X_k|\) = amplitude
# - \(\phi_k\) = phase
# - \(f_k=kf_s/N\) = frequency
# 
# The original signal can be reconstructed using
# 
# \[
# x_n =
# \frac1N
# \sum_{k=0}^{N-1}
# X_k e^{2\pi i kn/N}.
# \]
# 
# The app deliberately throws away most of the \(X_k\)'s and
# keeps only the strongest components.
# 
# Therefore you are hearing approximately
# 
# \[
# \hat{x}(t)
# =
# \sum_{k\in S}
# A_k\cos(2\pi f_k t+\phi_k).
# \]
# 
# The interesting experiment is to increase the number of
# components:
# 
# \[
# 5 \rightarrow 10 \rightarrow 20 \rightarrow 50
# \]
# 
# and listen to how the speech becomes progressively more
# recognizable.
# """
#     )
