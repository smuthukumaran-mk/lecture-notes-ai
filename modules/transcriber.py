from pathlib import Path

import streamlit as st
from faster_whisper import WhisperModel

from config import WHISPER_MODEL, TRANSCRIPT_DIR


@st.cache_resource
def load_model():
    """
    Load the Whisper model only once.
    """

    return WhisperModel(
        WHISPER_MODEL,
        device="cpu",
        compute_type="int8",
    )


def transcribe_audio(
    audio_path: Path,
    input_language: str,
) -> tuple[str, Path]:
    """
    Transcribe an audio file using Faster Whisper.
    """

    model = load_model()

    language_map = {
        "Auto Detect": None,
        "English": "en",
        "Tamil": "ta",
        "Hindi": "hi",
        "Telugu": "te",
        "Malayalam": "ml",
        "Kannada": "kn",
    }

    language = language_map.get(input_language)

    # More accurate for mixed-language lectures
    if language is None:
        segments, info = model.transcribe(
            str(audio_path),
            beam_size=3,
            vad_filter=True,
        )
    else:
        segments, info = model.transcribe(
            str(audio_path),
            language=language,
            beam_size=3,
            vad_filter=True,
        )

    transcript_parts = []

    for segment in segments:
        transcript_parts.append(segment.text.strip())

    transcript = " ".join(transcript_parts).strip()

    transcript_path = TRANSCRIPT_DIR / f"{audio_path.stem}.txt"

    with open(transcript_path, "w", encoding="utf-8") as file:
        file.write(transcript)

    return transcript, transcript_path