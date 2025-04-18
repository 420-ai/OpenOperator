import os

import logging
logger = logging.getLogger("init.utils")

def update_system_path(new_path):
    """Updates the system PATH variable (requires admin privileges)"""
    try:
        current_path = os.environ["PATH"]
        if new_path not in current_path:
            logger.info(f"Adding {new_path} to system PATH")
            # Append new_path to the current PATH
            updated_path = f"{current_path}{os.pathsep}{new_path}"
            # Use the /M flag to update the system (machine) environment variable
            subprocess.run(["setx", "/M", "PATH", updated_path], shell=True, check=True)
            logger.info(
                "System PATH updated successfully. A restart may be required for changes to take effect."
            )
        else:
            logger.info("The specified path is already in the PATH.")
    except Exception as e:
        logger.error(f"Failed to update PATH: {e}")

