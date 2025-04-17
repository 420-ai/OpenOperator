import sys
import os
import json
import requests
import subprocess
import logging
import pythoncom
import glob
import time
import shutil
from dotenv import load_dotenv

load_dotenv()

# Ensure COM is properly initialized
pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)

# Setup logging
logs_path = os.getenv("LOG_PATH")
print(f"Logs path:")
print(logs_path)

log_file = os.path.join(logs_path, "install_software.log")

print(f"Log file:")
print(log_file)

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Username
if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    username = "docker"

logging.info(f"Using USERNAME: {username}")


TEMP_DIR = r"C:\TEMP"
os.makedirs(TEMP_DIR, exist_ok=True)


def log(message):
    print(message)
    logging.info(message)


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


def update_system_path(new_path):
    """Updates the system PATH variable (requires admin privileges)"""
    try:
        current_path = os.environ["PATH"]
        if new_path not in current_path:
            print(f"Adding {new_path} to system PATH")
            # Append new_path to the current PATH
            updated_path = f"{current_path}{os.pathsep}{new_path}"
            # Use the /M flag to update the system (machine) environment variable
            subprocess.run(["setx", "/M", "PATH", updated_path], shell=True, check=True)
            print(
                "System PATH updated successfully. A restart may be required for changes to take effect."
            )
        else:
            print("The specified path is already in the PATH.")
    except Exception as e:
        print(f"Failed to update PATH: {e}")


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


def download_and_install(name, mirrors, tools_config):
    if name.lower() == "vs code":
        file_extension = "exe"
    elif name.lower() == "microsoft teams":
        file_extension = "msi"
    else:
        file_extension = mirrors[0].split(".")[-1]

    installer_path = os.path.join(TEMP_DIR, f"{name}_installer.{file_extension}")
    log(f"Downloading {name} ... into {installer_path}")

    for url in mirrors:
        try:
            response = requests.get(url, stream=True)
            with open(installer_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            log(f"{name} downloaded successfully.")
            break
        except Exception as e:
            log(f"Error downloading from {url}: {e}")
            logging.error(f"Error downloading {name} from {url}: {e}")
    else:
        log(f"Failed to download {name}.")
        return

    # FFMPEG
    if name.lower() == "ffmpeg":
        extract_dir = os.path.join(TEMP_DIR, "ffmpeg")
        if extract_ffmpeg(installer_path, extract_dir):
            ffmpeg_bin_path = find_ffmpeg_bin(extract_dir)
            if os.path.exists(ffmpeg_bin_path):
                update_system_path(ffmpeg_bin_path)
            else:
                log("Could not find ffmpeg binary folder after extraction.")
        else:
            log("Failed to extract ffmpeg.")

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
            log(f"Installing {name}...")
            try:
                subprocess.run([installer_path] + args, check=True)
                log(f"{name} installed successfully.")
            except subprocess.CalledProcessError as e:
                log(f"Installation failed for {name}: {e}")
                logging.error(f"Installation failed for {name}: {e}")

        elif file_extension == "msi":
            log(f"Installing {name} (MSI)...")
            try:
                subprocess.run(["msiexec", "/i", installer_path] + args, check=True)
                log(f"{name} installed successfully.")
            except subprocess.CalledProcessError as e:
                log(f"Installation failed for {name}: {e}")
                logging.error(f"Installation failed for {name}: {e}")

    # Time sleep for waiting until the installation process is released
    time.sleep(3)
    print(f"Removing {installer_path}")
    os.remove(installer_path)
    print(f"Removed {installer_path}")


def start_software_installation():
    json_path = os.path.join(os.path.dirname(__file__), "software.json")

    if not os.path.exists(json_path):
        log("JSON configuration file not found!")
        return

    with open(json_path, "r") as f:
        tools_config = json.load(f)

    for tool_name, details in tools_config.items():
        mirrors = details.get("mirrors", [])
        download_and_install(tool_name, mirrors, tools_config)

    log("All tasks completed.")


def install_playwright_chromium():
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
        logging.info("Playwright Chromium installed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Playwright Chromium installation failed: {e}")


def install_with_winget():
    try:
        subprocess.run(
            [
                "winget",
                "import",
                "--import-file",
                r"C:\Data\init\winget-software.json",
                "--accept-source-agreements",
                "--accept-package-agreements",
                "--disable-interactivity",
            ],
            check=True,
        )
        logging.info("bulk install with winget.")
    except subprocess.CalledProcessError as e:
        logging.error(f"winget installation failed: {e}")



def install_appium_cli():
    npm_path = shutil.which("npm") or r"C:\Program Files\nodejs\npm.cmd"
    if not os.path.exists(npm_path):
        logging.error("npm not found. Make sure Node.js is installed and npm is in PATH.")
        return

    try:
        command = [npm_path, "install", "-g", "appium"]
        logging.info(f"Installing Appium CLI with command: {command}")

        subprocess.run(command, check=True)
        logging.info("Appium CLI installed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Appium CLI installation failed: {e}")

def install_winappdriver_silent():
    wad_url = "https://github.com/microsoft/WinAppDriver/releases/download/v1.2.1/WindowsApplicationDriver_1.2.1.msi"
    wad_installer_path = os.path.join(TEMP_DIR, "WindowsApplicationDriver.msi")

    try:
        logging.info("Downloading WinAppDriver...")
        response = requests.get(wad_url, stream=True)
        with open(wad_installer_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info("WinAppDriver downloaded successfully.")

        logging.info("Installing WinAppDriver silently...")
        subprocess.run(["msiexec", "/i", wad_installer_path, "/quiet", "/norestart"], check=True)
        logging.info("WinAppDriver installed silently.")
        os.remove(wad_installer_path)
    except Exception as e:
        logging.error(f"Failed to install WinAppDriver: {e}")

def install_appium_drivers():
    appium_cmd = fr"C:\Users\{username}\AppData\Roaming\npm\appium.cmd"
    drivers = ["windows"]
    for drv in drivers:
        try:
            subprocess.run([appium_cmd, "driver", "install", drv], check=True)
            logging.info(f"Appium driver '{drv}' installed.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install Appium driver '{drv}': {e}")
    
    # Install WinAppDriver silently
    install_winappdriver_silent()

def enable_windows_developer_mode():
    try:
        subprocess.run([
            "reg",
            "add",
            r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock",
            "/t", "REG_DWORD",
            "/f",
            "/v", "AllowDevelopmentWithoutDevLicense",
            "/d", "1"
        ], check=True)
        logging.info("Windows Developer Mode enabled.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to enable Developer Mode: {e}")



def turn_on_teams_flags():
    try:
        # copy the "configuration.json" to the installation location: 
        teams_path = fr"\users\{username}\appdata\local\Packages\MSTeams_8wekyb3d8bbwe\LocalCache\Microsoft\MSTeams"
        teams_config_path = os.path.join(
            teams_path, "configuration.json"
        )

        shutil.copyfile(
            os.path.join(os.path.dirname(__file__), "configuration.json"),
            teams_config_path,
        )

    except Exception as e:
        logging.error(f"Failed to copy Teams configuration: {e}")
        raise
        
if __name__ == "__main__":
    try:
        logging.info("Starting Installer...")
        start_software_installation()
        logging.info("Software installation finished.")
        install_with_winget()
        logging.info("Winget installation finished.")
        
        install_appium_cli()
        install_appium_drivers()
        logging.info("Appium CLI installed successfully.")
        enable_windows_developer_mode()
        logging.info("Windows Developer Mode enabled.")

        install_playwright_chromium()
        logging.info("Installation completed successfully.")

        turn_on_teams_flags()
        logging.info("Teams flags turned on successfully.")
    except Exception as e:
        logging.error(f"Installation failed with error: {e}", exc_info=True)
    finally:
        pythoncom.CoUninitialize()  # Uninitialize COM when exiting
