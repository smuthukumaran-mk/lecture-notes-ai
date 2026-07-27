from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# --------------------------------------------------
# Base Directory
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# --------------------------------------------------
# Project Directories
# --------------------------------------------------

TRANSCRIPT_DIR = BASE_DIR / "transcript"
SUMMARY_DIR = BASE_DIR / "summary"

# Create directories automatically
for directory in (
    TRANSCRIPT_DIR,
    SUMMARY_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Whisper Configuration
# --------------------------------------------------

# Available models:
# tiny, base, small, medium, large-v3
WHISPER_MODEL = "medium"

# --------------------------------------------------
# Ollama Configuration
# --------------------------------------------------

# Model name can be overridden in .env
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

# Ollama server URL
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")