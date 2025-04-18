import os
import json
import logging
import requests
import subprocess
import time

from install_ffmpeg import extract_ffmpeg, find_ffmpeg_bin, update_system_path
from utils import update_system_path

logger = logging.getLogger("init.install_software")


def download_and_install(name, mirrors, tools_config, TEMP_DIR):
    if name.lower() == "vs code":
        file_extension = "exe"
    elif name.lower() == "microsoft teams":
        file_extension = "msi"
    else:
        file_extension = mirrors[0].split(".")[-1]

    installer_path = os.path.join(TEMP_DIR, f"{name}_installer.{file_extension}")
    logger.info(f"Downloading {name} ... into {installer_path}")

    for url in mirrors:
        try:
            response = requests.get(url, stream=True)
            with open(installer_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"{name} downloaded successfully.")
            break
        except Exception as e:
            logger.info(f"Error downloading from {url}: {e}")
            logger.error(f"Error downloading {name} from {url}: {e}")
    else:
        logger.info(f"Failed to download {name}.")
        return

    # FFMPEG
    if name.lower() == "ffmpeg":
        extract_dir = os.path.join(TEMP_DIR, "ffmpeg")
        if extract_ffmpeg(installer_path, extract_dir):
            ffmpeg_bin_path = find_ffmpeg_bin(extract_dir)
            if os.path.exists(ffmpeg_bin_path):
                update_system_path(ffmpeg_bin_path)
            else:
                logger.info("Could not find ffmpeg binary folder after extraction.")
        else:
            logger.info("Failed to extract ffmpeg.")

    # ANY OTHER SOFTWARE
    else:
        silent_args = {
            "git": ["/VERYSILENT", "/NORESTART"],
            "7zip": ["/S"],
            "google chrome": ["/silent", "/install"],
            "vs code": [
                "/VERYSILENT",
                "/mergetasks=!runcode",
                "/SUPPRESSMSGBOXES",
                "/NORESTART",
                "/SP-",
                "/ACCEPTEULA",
            ],
            "vlc": ["/S"],
            "microsoft teams": [
                "OPTIONS=noAutoStart=true",
                "ALLUSERS=1",
                "/quiet",
                "/norestart",
            ],
        }
        args = silent_args.get(name.lower(), ["/S"])

        if file_extension == "exe":
            logger.info(f"Installing {name}...")
            try:
                subprocess.run([installer_path] + args, check=True)
                logger.info(f"{name} installed successfully.")
            except subprocess.CalledProcessError as e:
                logger.info(f"Installation failed for {name}: {e}")
                logger.error(f"Installation failed for {name}: {e}")

        elif file_extension == "msi":
            logger.info(f"Installing {name} (MSI)...")
            try:
                subprocess.run(["msiexec", "/i", installer_path] + args, check=True)
                logger.info(f"{name} installed successfully.")
            except subprocess.CalledProcessError as e:
                logger.info(f"Installation failed for {name}: {e}")
                logger.error(f"Installation failed for {name}: {e}")

    # Time sleep for waiting until the installation process is released
    time.sleep(3)
    logger.info(f"Removing {installer_path}")
    os.remove(installer_path)
    logger.info(f"Removed {installer_path}")


def install_software(TEMP_DIR):
    json_path = os.path.join(os.path.dirname(__file__), "software.json")

    if not os.path.exists(json_path):
        logger.info("JSON configuration file not found!")
        return

    with open(json_path, "r") as f:
        tools_config = json.load(f)

    for tool_name, details in tools_config.items():
        mirrors = details.get("mirrors", [])
        download_and_install(tool_name, mirrors, tools_config, TEMP_DIR)

    logger.info("All tasks completed.")