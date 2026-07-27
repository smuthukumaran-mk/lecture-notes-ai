from pathlib import Path


def delete_temp_file(file_path):
    """
    Delete a temporary file if it exists.
    """

    try:

        file_path = Path(file_path)

        if file_path.exists():
            file_path.unlink()

    except Exception:
        pass