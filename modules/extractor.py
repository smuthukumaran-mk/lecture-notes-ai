from pathlib import Path
import tempfile
import uuid

import ffmpeg


SUPPORTED_AUDIO = {
    ".mp3",
    ".wav",
    ".m4a",
}


def extract_audio(file_path: Path) -> Path:
    """
    Extract audio from a video file.

    If the uploaded file is already an audio file,
    simply return it.
    """

    # Already an audio file
    if file_path.suffix.lower() in SUPPORTED_AUDIO:
        return file_path

    temp_dir = Path(tempfile.gettempdir())

    # Unique filename to avoid overwriting
    audio_path = temp_dir / f"{uuid.uuid4().hex}.wav"

    try:
        (
            ffmpeg
            .input(str(file_path))
            .output(
                str(audio_path),
                ac=1,                 # Mono
                ar=16000,             # Whisper sample rate
                acodec="pcm_s16le"    # 16-bit PCM WAV
            )
            .overwrite_output()
            .run(
                quiet=True,
                capture_stdout=True,
                capture_stderr=True,
            )
        )

    except ffmpeg.Error as e:

        error = ""

        if e.stderr:
            error = e.stderr.decode(errors="ignore")

        raise RuntimeError(
            f"FFmpeg failed to extract audio.\n{error}"
        )

    if not audio_path.exists():
        raise FileNotFoundError(
            "Audio extraction failed. Output file was not created."
        )

    return audio_path