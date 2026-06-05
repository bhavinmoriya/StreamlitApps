import os
import tempfile
import subprocess
import numpy as np
import soundfile as sf
import streamlit as st

# from demucs import translate
# from demucs.pretrained import get_model
# from demucs.separate import separate
from demucs.api import Separator
from demucs.pretrained import get_model

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

def load_audio(path: str):
    data, rate = sf.read(path)
    return data, rate

def save_audio(path: str, data: np.ndarray, rate: int) -> None:
    sf.write(path, data, rate)

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

def denoise_with_demucs(audio_in: str, audio_out: str) -> None:
    """
    Denoise audio using demucs (AI source separation).
    We separate into stems (vocals, other, drums, bass) and recombine them
    to get a cleaned version of the original audio.
    """
    import scipy.signal as sig
    import torch

    # Load audio (demucs expects float32, channels first, 44.1kHz)
    data, rate = sf.read(audio_in)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    else:
        data = data.T  # demucs expects (channels, time)

    if rate != 44100:
        num_samples = int(len(data[0]) * 44100 / rate)
        data = sig.resample(data[0], num_samples)
        data = data.reshape(1, -1)
        rate = 44100

    data = data.astype(np.float32)
    wav = torch.from_numpy(data)

    # Initialize Separator with htdemucs model
    separator = Separator("htdemucs", device="cpu", progress=True)

    # Separate
    _, stems = separator.separate(wav)

    # Recombine all stems
    total = sum(stems[stem] for stem in stems.keys())

    total = np.clip(total.numpy(), -1.0, 1.0)

    if total.ndim == 1:
        total = total.reshape(-1)
    else:
        total = total.mean(axis=0)  # mono

    # Resample to 16kHz for ffmpeg
    if rate != 16000:
        num_samples = int(len(total) * 16000 / rate)
        total = sig.resample(total, num_samples).astype(np.float32)
        rate = 16000

    save_audio(audio_out, total, rate)
    
# def denoise_with_demucs(audio_in: str, audio_out: str) -> None:
#     """
#     Denoise audio using demucs (AI source separation).
#     We separate into stems and recombine them to get a cleaned version.
#     """
#     import scipy.signal as sig
# 
#     # Ensure 44.1kHz for demucs
#     data, rate = sf.read(audio_in)
#     if rate != 44100:
#         num_samples = int(len(data) * 44100 / rate)
#         data = sig.resample(data, num_samples).astype(np.float32)
#         rate = 44100
# 
#     tmp_44 = audio_in + "_44.wav"
#     sf.write(tmp_44, data, rate)
# 
#     # Load model
#     model = get_model("htdemucs")
# 
#     # Create temp output dir
#     sep_dir = tempfile.mkdtemp()
# 
#     # Separate: uses the high-level separate function
#     separate(
#         model=model,
#         track=tmp_44,
#         output_dir=sep_dir,
#         verbose=False,
#     )
# 
#     # Find track folder
#     track_dir = None
#     for name in os.listdir(sep_dir):
#         path = os.path.join(sep_dir, name)
#         if os.path.isdir(path):
#             track_dir = path
#             break
#     if track_dir is None:
#         raise RuntimeError("demucs did not create a track folder.")
# 
#     # Sum all stems (vocal, other, drums, bass)
#     total = None
#     for stem in ["vocal", "other", "drums", "bass"]:
#         stem_path = os.path.join(track_dir, stem + ".wav")
#         if not os.path.exists(stem_path):
#             continue
#         stem_data, stem_rate = sf.read(stem_path)
#         if total is None:
#             total = stem_data
#         else:
#             if len(stem_data) != len(total):
#                 if len(stem_data) > len(total):
#                     stem_data = stem_data[:len(total)]
#                 else:
#                     stem_data = np.pad(stem_data, (0, len(total) - len(stem_data)))
#             total = total + stem_data
# 
#     if total is None:
#         raise RuntimeError("demucs produced no stems.")
# 
#     total = np.clip(total, -1.0, 1.0)
# 
#     # Resample to 16kHz mono for ffmpeg
#     if total.ndim > 1:
#         total = total.mean(axis=1)
#     if rate != 16000:
#         num_samples = int(len(total) * 16000 / rate)
#         total = sig.resample(total, num_samples).astype(np.float32)
#         rate = 16000
# 
#     save_audio(audio_out, total, rate)
# 
#     # Cleanup
#     for root, dirs, files in os.walk(sep_dir):
#         for f in files:
#             os.remove(os.path.join(root, f))
#         for d in dirs:
#             os.rmdir(os.path.join(root, d))
#     os.rmdir(sep_dir)
#     if os.path.exists(tmp_44):
#         os.remove(tmp_44)
        
# def denoise_with_demucs(audio_in: str, audio_out: str) -> None:
#     """
#     Denoise audio using demucs (AI source separation).
#     We separate vocals + ambient, then recombine cleaned audio.
#     This is a simple approach: separate vocals, then re-sum all tracks.
#     You can tune which tracks to keep.
#     """
#     # demucs works best with 44.1kHz WAV
#     rate_in, data_in = sf.read(audio_in)
#     if rate_in != 44100:
#         # resample to 44.1kHz
#         import scipy.signal as sig
#         num_samples = int(len(data_in) * 44100 / rate_in)
#         data_in = sig.resample(data_in, num_samples)
#         rate_in = 44100
# 
#     tmp_wav_44 = audio_in + "_44.wav"
#     sf.write(tmp_wav_44, data_in, rate_in)
# 
#     # Load demucs model
#     model = get_model("htdemucs")
# 
#     # Separate: creates tracks in a folder
#     # We'll use a temp dir for outputs
#     sep_dir = tempfile.mkdtemp()
#     out_wav = os.path.join(sep_dir, "audio_demucs.wav")
# 
#     # demucs separate function
#     # track: path to audio
#     # output_dir: where to write tracks
#     # verbose: False
#     separate(
#         model=model,
#         track=tmp_wav_44,
#         output_dir=sep_dir,
#         verbose=False,
#     )
# 
#     # demucs writes tracks like: <name>/vocal.wav, <name>/other.wav, etc.
#     # We'll re-sum all tracks into a single cleaned audio.
#     # Find the track folder (first subdirectory)
#     track_dir = None
#     for name in os.listdir(sep_dir):
#         path = os.path.join(sep_dir, name)
#         if os.path.isdir(path):
#             track_dir = path
#             break
# 
#     if track_dir is None:
#         raise RuntimeError("demucs did not create a track folder.")
# 
#     # Load all tracks and sum
#     total = None
#     for track_name in ["vocal", "other", "drums", "bass"]:
#         track_path = os.path.join(track_dir, track_name + ".wav")
#         if not os.path.exists(track_path):
#             continue
#         data, rate = sf.read(track_path)
#         if total is None:
#             total = data
#         else:
#             # align lengths
#             if len(data) != len(total):
#                 data = data[:len(total)] if len(data) > len(total) else np.pad(data, (0, len(total)-len(data)))
#             total = total + data
# 
#     if total is None:
#         raise RuntimeError("demucs did not produce any tracks.")
# 
#     total = np.clip(total, -1.0, 1.0)
# 
#     # Save as 16kHz mono WAV for ffmpeg
#     if rate != 16000:
#         import scipy.signal as sig
#         num_samples = int(len(total) * 16000 / rate)
#         total = sig.resample(total, num_samples)
#         rate = 16000
# 
#     save_audio(audio_out, total, rate)
# 
#     # Clean up temp demucs dir
#     for f in os.listdir(sep_dir):
#         fp = os.path.join(sep_dir, f)
#         if os.path.isfile(fp):
#             os.remove(fp)
#         elif os.path.isdir(fp):
#             for tf in os.listdir(fp):
#                 os.remove(os.path.join(fp, tf))
#             os.rmdir(fp)
#     os.rmdir(sep_dir)
#     if os.path.exists(tmp_wav_44):
#         os.remove(tmp_wav_44)

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
    noise_method: str = "rnnoise",
    whisper_model: str = "base"
) -> None:
    """
    noise_method: "rnnoise" or "demucs"
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_in = os.path.join(tmpdir, "audio_raw.wav")
        audio_clean = os.path.join(tmpdir, "audio_clean.wav")

        # 1. Extract audio
        extract_audio(video_path, audio_in)

        # 2. Denoise audio
        if noise_method == "rnnoise":
            denoise_with_rnnoise(audio_in, audio_clean)
        elif noise_method == "demucs":
            denoise_with_demucs(audio_in, audio_clean)
        else:
            raise ValueError(f"Unknown noise_method: {noise_method}")

        # 3. Optional transcription
        if output_txt_path is not None:
            if not WHISPER_AVAILABLE:
                raise RuntimeError("Whisper not available but transcription requested.")
            transcribe_with_whisper(audio_clean, output_txt_path, model_name=whisper_model)

        # 4. Create vertical short with cleaned audio
        crop_to_short(video_path, output_short_path, audio_clean)

# Streamlit UI
st.title("Clean Audio + YouTube Short Generator (with choices)")
st.markdown("""
Upload a video. This app will:
- Remove noise from the audio (choose method)
- Crop to a vertical 9:16 YouTube Short (1080×1920)
- Optionally add Whisper transcription as a .txt sidecar file
- Return the cleaned short + optional .txt
""")

uploaded = st.file_uploader("Upload video", type=["mp4", "mov", "avi", "mkv"])

noise_method = st.radio(
    "Noise removal method",
    options=["rnnoise (ffmpeg)", "demucs (AI)"],
    index=0,
    help="""
    - rnnoise: Fast, uses ffmpeg filter. Good for general noise.
    - demucs: AI-based source separation, heavier but often better quality.
    """
)

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
                        noise_method=noise_method.replace(" (ffmpeg)", "").replace(" (AI)", ""),
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
