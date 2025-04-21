import sys
import subprocess

import logging
logger = logging.getLogger("init.install_playwright")

def install_playwright():
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
        logger.info("Playwright Chromium installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Playwright Chromium installation failed: {e}")

