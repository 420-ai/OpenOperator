import subprocess

import logging
logger = logging.getLogger("init.enable_developer_mode")

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
        logger.info("Windows Developer Mode enabled.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to enable Developer Mode: {e}")
