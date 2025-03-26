import os
from typing import List


def delete_files(paths: List[str]):
    """
    Delete files from the filesystem.

    Args:
        paths (List[str]): List of file paths to delete.
    """
    for path in paths:
        try:
            if os.path.isfile(path):
                os.remove(path)
                print(f"Deleted file: {path}")
            else:
                print(f"File not found: {path}")
        except Exception as e:
            print(f"Error deleting file {path}: {e}")
