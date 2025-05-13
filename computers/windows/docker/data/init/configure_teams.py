import os
import shutil

import logging
logger = logging.getLogger("init.configure_teams")

def configure_teams(username: str):
    try:
        # copy the "configuration.json" to the installation location: 
        teams_path = fr"\users\{username}\AppData\local\Packages\MSTeams_8wekyb3d8bbwe\LocalCache\Microsoft\MSTeams"
        teams_config_path = os.path.join(
            teams_path, "configuration.json"
        )

        logger.info(f"Teams configuration path: {teams_config_path}")

        # Ensure the Teams path exists
        os.makedirs(os.path.dirname(teams_config_path), exist_ok=True)

        # OO config file
        ooconfig_path = os.path.join(
            os.path.dirname(__file__), "configuration.json"
        )

        logger.info(f"OO config path: {ooconfig_path}")

        # does the file exist?
        if not os.path.exists(ooconfig_path):
            logger.error(f"Configuration file {ooconfig_path} does not exist.")
            raise FileNotFoundError(f"Configuration file {ooconfig_path} does not exist.")

        shutil.copyfile(
            ooconfig_path,
            teams_config_path,
        )

        logger.info(f"Teams configuration copied from {ooconfig_path} to {teams_config_path}")

    except Exception as e:
        logger.error(f"Failed to copy Teams configuration: {e}")
        raise
        