import streamlit as st
import librosa
import soundfile as sf
import os
import tempfile
import numpy as np

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

    # Create a temporary directory to save files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save the uploaded MP3 file temporarily
        mp3_path = os.path.join(temp_dir, uploaded_file.name)
        with open(mp3_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            # Load MP3 file using librosa
            y, sr = librosa.load(mp3_path, sr=None)

            # Save as WAV using soundfile
            wav_path = os.path.join(temp_dir, "output.wav")
            sf.write(wav_path, y, sr)

            # Provide download button for the WAV file
            st.success("Conversion successful!")
            with open(wav_path, "rb") as f:
                st.download_button(
                    label="Download WAV File",
                    data=f,
                    file_name="output.wav",
                    mime="audio/wav"
                )

            # Optional: Play the converted audio
            st.audio(wav_path, format="audio/wav")

        except Exception as e:
            st.error(f"Error during conversion: {e}")
