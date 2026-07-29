import streamlit as st
from pydub import AudioSegment
import os
import tempfile

# App title
st.title("🎵 MP3 to WAV Converter")
st.write("Upload an MP3 file to convert it to WAV format.")

# File uploader
uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])

if uploaded_file is not None:
    # Display uploaded file info
    st.success(f"File uploaded: {uploaded_file.name}")

    # Create a temporary directory to save files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save the uploaded MP3 file temporarily
        mp3_path = os.path.join(temp_dir, uploaded_file.name)
        with open(mp3_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Convert MP3 to WAV
        try:
            audio = AudioSegment.from_mp3(mp3_path)
            wav_path = os.path.join(temp_dir, "output.wav")
            audio.export(wav_path, format="wav")

            # Provide download button for the WAV file
            st.success("Conversion successful!")
            with open(wav_path, "rb") as f:
                st.download_button(
                    label="Download WAV File",
                    data=f,
                    file_name="output.wav",
                    mime="audio/wav"
                )
        except Exception as e:
            st.error(f"Error during conversion: {e}")
