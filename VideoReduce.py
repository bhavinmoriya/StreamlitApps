import streamlit as st
import subprocess
import os
from tempfile import NamedTemporaryFile

st.title("FFmpeg H.265 Video Converter")
st.write("Upload a video file to convert it to H.265 (libx265) with CRF 28.")

# Upload the input video file
input_file = st.file_uploader("Upload your video file (e.g., OTPORSApp.mp4)", type=["mp4"])

if input_file:
    # Save the uploaded file to a temporary location
    with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
        temp_input.write(input_file.read())
        temp_input_path = temp_input.name

    # Define the output file path
    output_path = "output.mp4"

    # Display a preview of the input video (optional)
    st.video(input_file)

    # Convert button
    if st.button("Convert to H.265 (libx265)"):
        with st.spinner("Converting video..."):
            try:
                # Run ffmpeg command
                command = [
                    "ffmpeg",
                    "-i", temp_input_path,
                    "-vcodec", "libx265",
                    "-crf", "28",
                    "-y",  # Overwrite output file if it exists
                    output_path
                ]
                subprocess.run(command, check=True, stderr=subprocess.PIPE)

                # Display success message
                st.success("Video converted successfully!")

                # Provide download link for the output file
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="Download Converted Video",
                        data=f,
                        file_name="output.mp4",
                        mime="video/mp4"
                    )
            except subprocess.CalledProcessError as e:
                st.error(f"Error during conversion: {e.stderr.decode()}")
            finally:
                # Clean up temporary files
                if os.path.exists(temp_input_path):
                    os.remove(temp_input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)

linkedin_url = "https://www.linkedin.com/in/bhavin-moriya-ph-d-b0b88b2/"
github_url = "https://github.com/bhavinmoriya"

st.markdown("## Connect with me")

col1, col2 = st.columns(2)

with col1:
    st.link_button("🔗 Follow on LinkedIn", linkedin_url)

with col2:
    st.link_button("💻 Follow on GitHub", github_url)
