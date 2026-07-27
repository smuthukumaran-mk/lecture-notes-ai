from pathlib import Path
import tempfile


def save_uploaded_file(uploaded_file) -> Path:
    """
    Save uploaded file to the OS temporary directory.
    """

    temp_dir = Path(tempfile.gettempdir())

    file_path = temp_dir / uploaded_file.name

    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return file_path