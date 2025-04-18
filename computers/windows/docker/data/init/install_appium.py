import os
import shutil
import subprocess
import requests

import logging
logger = logging.getLogger("init.install_appium")

def install_appium_cli():
    npm_path = shutil.which("npm") or r"C:\Program Files\nodejs\npm.cmd"
    if not os.path.exists(npm_path):
        logger.error("npm not found. Make sure Node.js is installed and npm is in PATH.")
        return

    try:
        command = [npm_path, "install", "-g", "appium"]
        logger.info(f"Installing Appium CLI with command: {command}")

        subprocess.run(command, check=True)
        logger.info("Appium CLI installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Appium CLI installation failed: {e}")

def is_appium_driver_installed(driver_name, appium_cmd):
    try:
        result = subprocess.run(
            [appium_cmd, "driver", "list", "--installed"],
            capture_output=True, text=True, check=True
        )
        return driver_name.lower() in result.stdout.lower()
    except subprocess.CalledProcessError as e:
        logger.warning(f"Could not check if Appium driver '{driver_name}' is installed: {e}")
        return False

def install_appium_drivers(username):
    appium_cmd = fr"C:\Users\{username}\AppData\Roaming\npm\appium.cmd"
    drivers = ["windows"]

    for drv in drivers:
        if is_appium_driver_installed(drv, appium_cmd):
            logger.info(f"Appium driver '{drv}' is already installed. Skipping.")
            continue

        try:
            subprocess.run([appium_cmd, "driver", "install", drv], check=True)
            logger.info(f"Appium driver '{drv}' installed.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Appium driver '{drv}': {e}")


def install_winappdriver_silent(TEMP_DIR):
    wad_url = "https://github.com/microsoft/WinAppDriver/releases/download/v1.2.1/WindowsApplicationDriver_1.2.1.msi"
    wad_installer_path = os.path.join(TEMP_DIR, "WindowsApplicationDriver.msi")

    try:
        logger.info("Downloading WinAppDriver...")
        response = requests.get(wad_url, stream=True)
        with open(wad_installer_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info("WinAppDriver downloaded successfully.")

        logger.info("Installing WinAppDriver silently...")
        subprocess.run(["msiexec", "/i", wad_installer_path, "/quiet", "/norestart"], check=True)
        logger.info("WinAppDriver installed silently.")
        os.remove(wad_installer_path)
    except Exception as e:
        logging.error(f"Failed to install WinAppDriver: {e}")


def install_appium(TEMP_DIR, username):
    logger.info("Installing Appium CLI ...")
    install_appium_cli()
    logger.info("Installing Appium drivers ...")
    install_appium_drivers(username)
    logger.info("Installing WinAppDriver ...")
    install_winappdriver_silent(TEMP_DIR)