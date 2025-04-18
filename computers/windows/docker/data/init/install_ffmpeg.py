
def extract_ffmpeg(archive_path, extract_to):
    """Extracts ffmpeg using 7-Zip"""
    seven_zip_path = r"C:\Program Files\7-Zip\7z.exe"

    if not os.path.exists(seven_zip_path):
        log(
            "7-Zip is required but not found in the expected path. Install 7-Zip first."
        )
        return False

    try:
        subprocess.run(
            [seven_zip_path, "x", archive_path, f"-o{extract_to}", "-y"], check=True
        )
        log(f"Extracted ffmpeg to {extract_to}")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Error extracting ffmpeg: {e}")
        return False


def find_ffmpeg_bin(root_dir):
    """Searches for the 'bin' folder inside any 'ffmpeg*' extracted folder."""
    ffmpeg_folders = glob.glob(os.path.join(root_dir, "ffmpeg*"))

    if not ffmpeg_folders:
        return None  # No ffmpeg folder found

    for folder in ffmpeg_folders:
        bin_path = os.path.join(folder, "bin")
        if os.path.exists(bin_path) and os.path.isfile(
            os.path.join(bin_path, "ffmpeg.exe")
        ):
            return bin_path  # Found the correct bin folder

    return None  # No valid bin folder found

