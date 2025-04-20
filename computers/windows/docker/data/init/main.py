import sys
import os
import pythoncom
import logging
from logging_setup import configure_logging
from dotenv import load_dotenv

load_dotenv()

# Ensure COM is properly initialized
pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)

# Setup logging
logs_path = os.getenv("LOG_PATH")
print("LOG_PATH", logs_path)
configure_logging(logs_path)
logger = logging.getLogger("init")
print("Logging configured")


# Username
if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    username = "docker"

logger.info(f"Using USERNAME: {username}")


TEMP_DIR = r"C:\TEMP"
os.makedirs(TEMP_DIR, exist_ok=True)


# import scripts
from install_software import install_software
from install_winget import install_winget
from verify_node_npm import verify_node_and_npm
from install_appium import install_appium
from enable_developer_mode import enable_windows_developer_mode
from install_playwright import install_playwright
from configure_teams import configure_teams
# from install_mitmproxy_certs import install_mitmproxy_certs

if __name__ == "__main__":
    try:
        logger.info("Installing software from software.json ...")
        install_software(TEMP_DIR)
        logger.info("Software installation finished.")
        logger.info("Installing software via WinGet ...")
        install_winget()
        logger.info("Winget installation finished.")
        
        logger.info("Verifying Node.js and npm ...")
        isNodeNpmReady = verify_node_and_npm()
        logger.info("Node.js and npm verification finished.")

        if isNodeNpmReady:
            logger.info("Node.js and npm are ready.")

            logger.info("Installing Appium ...")
            install_appium(TEMP_DIR, username)
            logger.info("Appium installed successfully.")
        else:
            logger.error("Node.js or npm is not ready. Please check the installation.")
            logger.error("Skipping Appium installation due to missing Node.js or npm.")

        
        logger.info("Enabling Windows Developer Mode ...")
        enable_windows_developer_mode()
        logger.info("Windows Developer Mode enabled.")

        logger.info("Installing Playwright Chromium ...")
        install_playwright()
        logger.info("Playwright Chromium installed successfully.")
        
        # logger.info("Setting up Teams configuration ...")
        # configure_teams(username)
        # logger.info("Teams configuration setup finished.")
    except Exception as e:
        logger.error(f"Installation failed with error: {e}", exc_info=True)
    finally:
        pythoncom.CoUninitialize()  # Uninitialize COM when exiting
