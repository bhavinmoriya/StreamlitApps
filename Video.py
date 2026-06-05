import os
import tempfile
import subprocess
import streamlit as st

# Whisper (optional)
try:
    import whisper
    WHISPER_AVAILABLE = True
except Exception:
    WHISPER_AVAILABLE = False
    st.warning("Whisper not available. Transcription will be disabled.")

def run_ffmpeg(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")
    return result

def extract_audio(video_path: str, audio_path: str) -> None:
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ]
    run_ffmpeg(cmd)

def denoise_with_rnnoise(audio_in: str, audio_out: str) -> None:
    """
    Denoise audio using ffmpeg's rnnoise filter.
    Input: mono WAV, 16kHz recommended.
    Output: mono WAV, same rate.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", audio_in,
        "-af", "rnnoise",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_out
    ]
    run_ffmpeg(cmd)

def crop_to_short(video_path: str, output_path: str, audio_path: str) -> None:
    w, h = 1080, 1920
    video_filter = (
        f"crop=ih*(9/16):ih, "
        f"scale={w}:{h}:flags=lanczos"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-filter:v", video_filter,
        "-c:a", "aac",
        "-b:a", "192k",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "22",
        "-r", "30",
        "-shortest",
        output_path
    ]
    run_ffmpeg(cmd)

def transcribe_with_whisper(audio_path: str, txt_path: str, model_name: str = "base") -> None:
    if not WHISPER_AVAILABLE:
        raise RuntimeError("Whisper not available.")
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path)
    text = result["text"]
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

def process_video_to_short(
    video_path: str,
    output_short_path: str,
    output_txt_path: str | None,
    whisper_model: str = "base"
) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_in = os.path.join(tmpdir, "audio_raw.wav")
        audio_clean = os.path.join(tmpdir, "audio_clean.wav")

        # 1. Extract audio
        extract_audio(video_path, audio_in)

        # 2. Denoise audio with rnnoise
        denoise_with_rnnoise(audio_in, audio_clean)

        # 3. Optional transcription
        if output_txt_path is not None:
            if not WHISPER_AVAILABLE:
                raise RuntimeError("Whisper not available but transcription requested.")
            transcribe_with_whisper(audio_clean, output_txt_path, model_name=whisper_model)

        # 4. Create vertical short with cleaned audio
        crop_to_short(video_path, output_short_path, audio_clean)

# Streamlit UI
st.title("Clean Audio + YouTube Short Generator (rnnoise only)")
st.markdown("""
Upload a video. This app will:
- Remove noise from the audio using ffmpeg's rnnoise filter
- Crop to a vertical 9:16 YouTube Short (1080×1920)
- Optionally add Whisper transcription as a .txt sidecar file
- Return the cleaned short + optional .txt
""")

uploaded = st.file_uploader("Upload video", type=["mp4", "mov", "avi", "mkv"])

do_transcript = st.checkbox(
    "Add Whisper transcription (.txt sidecar)",
    value=False,
    help="Transcribe the cleaned audio using OpenAI Whisper and provide a .txt file."
)

whisper_model = None
if do_transcript:
    if not WHISPER_AVAILABLE:
        st.warning("Whisper is not available. Transcription is disabled.")
        do_transcript = False
    else:
        whisper_model = st.selectbox(
            "Whisper model",
            options=["tiny", "base", "small", "medium"],
            index=1,  # default "base"
            help="Larger models are more accurate but slower."
        )

if uploaded is not None:
    if st.button("Process video"):
        with tempfile.TemporaryDirectory() as tmpdir:
            in_video = os.path.join(tmpdir, "input.mp4")
            out_short = os.path.join(tmpdir, "output_short.mp4")
            out_txt = os.path.join(tmpdir, "transcription.txt") if do_transcript else None

            with open(in_video, "wb") as f:
                f.write(uploaded.read())

            try:
                with st.spinner("Processing video (this may take a minute)..."):
                    process_video_to_short(
                        video_path=in_video,
                        output_short_path=out_short,
                        output_txt_path=out_txt,
                        whisper_model=whisper_model
                    )

                st.success("Done! Your clean YouTube Short is ready.")

                # Show video
                with open(out_short, "rb") as f:
                    video_bytes = f.read()
                st.video(video_bytes)

                st.download_button(
                    label="Download clean YouTube Short",
                    data=video_bytes,
                    file_name="clean_short.mp4",
                    mime="video/mp4"
                )

                # Show + download transcription if requested
                if do_transcript and out_txt and os.path.exists(out_txt):
                    with open(out_txt, "r", encoding="utf-8") as f:
                        txt_text = f.read()
                    st.text_area("Transcription (.txt)", value=txt_text, height=200)
                    with open(out_txt, "rb") as f:
                        txt_bytes = f.read()
                    st.download_button(
                        label="Download transcription (.txt)",
                        data=txt_bytes,
                        file_name="transcription.txt",
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"Error: {e}")
