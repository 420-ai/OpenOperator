import os
import shutil
import subprocess
import requests
import re

import logging
logger = logging.getLogger("init.install_appium")


def is_appium_installed_via_npm():
    try:
        result = subprocess.run(
            ["npm", "list", "-g"],
            shell=True,
            capture_output=True, text=True, check=True
        )
        return "appium@" in result.stdout.lower()
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to check Appium installation via npm: {e}")
        return False

def ensure_appium_cli_ready():
    if not is_appium_installed_via_npm():
        logger.info("Appium CLI not found via npm. Installing...")
        install_appium_cli()
    else:
        logger.info("Appium CLI is already installed via npm.")

def is_winappdriver_installed():
    # Default install path, change as needed
    wad_path = r"C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe"
    return os.path.exists(wad_path)


def is_appium_driver_installed(driver_name, appium_cmd):
    try:
        result = subprocess.run(
            [appium_cmd, "driver", "list", "--installed"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True,
            check=True
        )
        raw_output  = result.stdout
        logger.debug("RAW repr(output): " + repr(raw_output ))

        def strip_ansi_codes(text: str) -> str:
            return re.sub(r'\x1b\[[0-9;]*m', '', text)

        output = strip_ansi_codes(raw_output)
        logger.debug("Cleaned output:\n" + output)

        if f"- {driver_name.lower()}@" in output.lower():
            logger.info(f"Found installed Appium driver '{driver_name}'")
            return True

        return False
    except subprocess.CalledProcessError as e:
        logger.warning(f"Could not check if Appium driver '{driver_name}' is installed: {e}")
        return False


def install_appium_cli():
    try:
        command = ["npm", "install", "-g", "appium"]
        logger.info(f"Installing Appium CLI with command: {command}")

        subprocess.run(command, shell=True, check=True)
        logger.info("Appium CLI installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Appium CLI installation failed: {e}")

def install_appium_drivers(username):
    appium_cmd = fr"C:\Users\{username}\AppData\Roaming\npm\appium.cmd"
    drivers = ["windows"]

    for drv in drivers:
        if is_appium_driver_installed(drv, appium_cmd):
            logger.info(f"Appium driver '{drv}' is already installed. Skipping.")
            continue

        try:
            subprocess.run([appium_cmd, "driver", "install", drv], shell=True, check=True)
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

    # Install Appium CLI
    ensure_appium_cli_ready()
    
    # Install Appium drivers
    install_appium_drivers(username)

    # Install WinAppDriver
    if not is_winappdriver_installed():
        logger.info("WinAppDriver not found. Installing...")
        install_winappdriver_silent(TEMP_DIR)
    else:
        logger.info("WinAppDriver is already installed.")