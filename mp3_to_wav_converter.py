import streamlit as st
import librosa
import soundfile as sf
import os
import tempfile
import io

# App title
st.title("🎵 MP3 to WAV Converter (Librosa)")
st.write("Upload an MP3 file to convert it to WAV format using Librosa.")

# Add a clickable link
st.markdown(
    "Try decomposing sound with FFT: [Decompose Sound with FFT](https://decompose-sound-fft.streamlit.app/)"
)

# File uploader
uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])

if uploaded_file is not None:
    st.success(f"File uploaded: {uploaded_file.name}")

    try:
        # Load MP3 file directly from the uploaded bytes
        y, sr = librosa.load(io.BytesIO(uploaded_file.read()), sr=None)

        # Save the WAV file to a BytesIO buffer
        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, y, sr, format="WAV")
        wav_buffer.seek(0)  # Rewind the buffer to the start

        # Provide download button for the WAV file
        st.success("Conversion successful!")
        st.download_button(
            label="⬇️ Download WAV File",
            data=wav_buffer,
            file_name="output.wav",
            mime="audio/wav"
        )

        # Optional: Play the converted audio
        st.audio(wav_buffer, format="audio/wav")

    except Exception as e:
        st.error(f"Error during conversion: {e}")

linkedin_url = "https://www.linkedin.com/in/bhavin-moriya-ph-d-b0b88b2/"
github_url = "https://github.com/bhavinmoriya"

st.markdown("## Connect with me")

col1, col2 = st.columns(2)

with col1:
    st.link_button("🔗 Follow on LinkedIn", linkedin_url)

with col2:
    st.link_button("💻 Follow on GitHub", github_url)
