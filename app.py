from modules.cleanup import delete_temp_file
import time
from pathlib import Path

import streamlit as st

from modules.utils import save_uploaded_file
from modules.extractor import extract_audio
from modules.transcriber import transcribe_audio
from modules.summarizer import summarize_text

from modules.exporter import (
    export_pdf,
    export_docx,
)

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Lecture Notes AI",
    page_icon="📚",
    layout="wide",
)

# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("📚 Lecture Notes AI")
st.caption(
    "Convert lecture recordings into structured study notes using Whisper and Ollama."
)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.header("⚙️ Settings")

    st.info(
        """
Upload a lecture recording and automatically:

🎤 Extract audio

📝 Transcribe speech

🤖 Generate study notes

📄 Export as PDF, Word or Markdown
"""
    )

    st.divider()

    st.markdown(
        """
### Supported Formats

**Video**

- MP4
- AVI
- MOV
- MKV

**Audio**

- MP3
- WAV
- M4A
"""
    )

# --------------------------------------------------
# Session State
# --------------------------------------------------

if "result" not in st.session_state:
    st.session_state.result = None

if "current_signature" not in st.session_state:
    st.session_state.current_signature = None

# --------------------------------------------------
# File Upload
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "📂 Upload Lecture Recording",
    type=[
        "mp4",
        "avi",
        "mov",
        "mkv",
        "mp3",
        "wav",
        "m4a",
    ],
)

# Reset previous results when a new file is uploaded

current_signature = (
    (uploaded_file.name, uploaded_file.size)
    if uploaded_file
    else None
)

if current_signature != st.session_state.current_signature:
    st.session_state.result = None
    st.session_state.current_signature = current_signature

# --------------------------------------------------
# Processing Options
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    input_language = st.selectbox(
        "🎙️ Lecture Language",
        [
            "Auto Detect",
            "English",
            "Tamil",
            "Hindi",
            "Telugu",
            "Malayalam",
            "Kannada",
        ],
        index=0,
    )

with col2:

    output_language = st.selectbox(
        "🌍 Notes Language",
        [
            "Auto (Same as Lecture)",
            "English",
            "Tamil",
            "Hindi",
            "Telugu",
            "Malayalam",
            "Kannada",
        ],
        index=0,
    )

# --------------------------------------------------
# Export Options
# --------------------------------------------------

export_type = st.selectbox(
    "📄 Export Format",
    [
        "PDF",
        "Word",
        "Markdown",
    ],
)

st.divider()

# --------------------------------------------------
# Start Processing
# --------------------------------------------------

if uploaded_file:

    st.success("✅ File uploaded successfully.")

    file_size = uploaded_file.size / (1024 * 1024)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("File Name", uploaded_file.name)

    with col2:
        st.metric("File Size", f"{file_size:.2f} MB")

    with col3:
        st.metric("Export", export_type)

    process_button = st.button(
        "🚀 Generate Notes",
        type="primary",
        use_container_width=True,
    )

    if process_button:
        start_time = time.time()

        saved_path = None
        audio_path = None

        try:

            progress = st.progress(0)
            status = st.empty()

            # -----------------------------
            # Upload
            # -----------------------------

            status.info("📤 Saving uploaded file...")
            progress.progress(10)

            saved_path = save_uploaded_file(uploaded_file)

            # -----------------------------
            # Audio Extraction
            # -----------------------------

            status.info("🎵 Extracting audio...")
            progress.progress(25)

            audio_path = extract_audio(saved_path)

            # -----------------------------
            # Speech-to-Text
            # -----------------------------

            status.info("📝 Transcribing lecture...")

            progress.progress(45)

            transcript, transcript_path = transcribe_audio(
                audio_path,
                input_language,
            )

            if not transcript.strip():

                raise RuntimeError(
                    "No speech could be detected in the uploaded recording."
                )

            transcript_words = len(transcript.split())
            transcript_characters = len(transcript)

            # -----------------------------
            # Summarization
            # -----------------------------

            status.info("🤖 Generating study notes...")

            progress.progress(75)

            summary, summary_path = summarize_text(
                transcript,
                saved_path.stem,
                output_language,
            )

            summary_words = len(summary.split())

            # -----------------------------
            # Export
            # -----------------------------

            status.info("📄 Creating export file...")

            progress.progress(90)

            if export_type == "PDF":

                output_file = export_pdf(summary)

                download_name = f"{saved_path.stem}.pdf"

            elif export_type == "Word":

                output_file = export_docx(summary)

                download_name = f"{saved_path.stem}.docx"

            else:

                output_file = summary.encode("utf-8")

                download_name = f"{saved_path.stem}.md"

            processing_time = time.time() - start_time

            progress.progress(100)

            status.success("✅ Lecture processed successfully!")

            time.sleep(1)

            progress.empty()
            status.empty()

            # -----------------------------
            # Save Session State
            # -----------------------------

            st.session_state.result = {

                "summary": summary,

                "transcript": transcript,

                "summary_path": summary_path,

                "transcript_path": transcript_path,

                "output_file": output_file,

                "download_name": download_name,

                "saved_path": saved_path,

                "audio_path": audio_path,

                "file_name": uploaded_file.name,

                "file_type": uploaded_file.type,

                "file_size": uploaded_file.size,

                "export_type": export_type,

                "input_language": input_language,

                "output_language": output_language,

                "processing_time": processing_time,

                "transcript_words": transcript_words,

                "transcript_characters": transcript_characters,

                "summary_words": summary_words,
            }

        except Exception as e:

            st.error("❌ Processing failed.")

            with st.expander(
                "Technical Details"
            ):

                st.exception(e)

        finally:

            if saved_path:

                delete_temp_file(saved_path)

            if (
                audio_path
                and audio_path != saved_path
            ):

                delete_temp_file(audio_path)


    # --------------------------------------------------
    # Display Results
    # --------------------------------------------------

    if st.session_state.result:

        result = st.session_state.result

        st.success("🎉 Lecture processed successfully!")

        # ==================================================
        # Processing Summary
        # ==================================================

        st.subheader("📊 Processing Summary")

        metric1, metric2, metric3, metric4 = st.columns(4)

        with metric1:
            st.metric(
                "Processing Time",
                f"{result['processing_time']:.1f} sec",
            )

        with metric2:
            st.metric(
                "Transcript Words",
                result["transcript_words"],
            )

        with metric3:
            st.metric(
                "Summary Words",
                result["summary_words"],
            )

        with metric4:
            st.metric(
                "Export",
                result["export_type"],
            )

        st.divider()

        # ==================================================
        # File Details
        # ==================================================

        st.subheader("📄 File Information")

        left, right = st.columns(2)

        with left:

            st.write(
                f"**File Name:** {result['file_name']}"
            )

            st.write(
                f"**File Type:** {result['file_type']}"
            )

            st.write(
                f"**Input Language:** {result['input_language']}"
            )

        with right:

            st.write(
                f"**Output Language:** {result['output_language']}"
            )

            st.write(
                f"**File Size:** {result['file_size'] / (1024 * 1024):.2f} MB"
            )

            st.write(
                f"**Transcript Characters:** {result['transcript_characters']}"
            )

        st.divider()

        # ==================================================
        # Transcript
        # ==================================================

        with st.expander(
            "📝 View Transcript",
            expanded=False,
        ):

            st.text_area(
                "Transcript",
                result["transcript"],
                height=350,
            )

            st.caption(
                f"Saved to: {result['transcript_path']}"
            )

        # ==================================================
        # Study Notes
        # ==================================================

        st.subheader("📚 Generated Study Notes")

        with st.container():

            st.markdown(result["summary"])

        st.divider()

        # ==================================================
        # Markdown Copy
        # ==================================================

        with st.expander(
            "📋 View Markdown Source",
            expanded=False,
        ):

            st.code(
                result["summary"],
                language="markdown",
            )

        # ==================================================
        # Download
        # ==================================================

        st.subheader("📥 Download")

        st.download_button(

            label=f"⬇️ Download {result['export_type']}",

            data=result["output_file"],

            file_name=result["download_name"],

            use_container_width=True,

        )

        st.caption(
            f"Summary saved to: {result['summary_path']}"
        )

        st.divider()

        # ==================================================
        # Final Information
        # ==================================================

        st.info(
            f"""
    ### ✅ Processing Completed Successfully

    **Lecture Language:** {result['input_language']}

    **Notes Language:** {result['output_language']}

    **Export Format:** {result['export_type']}

    **Processing Time:** {result['processing_time']:.1f} seconds

    Your lecture has been successfully:

    - 🎵 Converted to audio
    - 📝 Transcribed using Faster Whisper
    - 🤖 Summarized using Ollama
    - 📄 Exported successfully

    Happy Learning! 📚
    """
        )    