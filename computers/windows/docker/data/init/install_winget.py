import subprocess
import logging
logger = logging.getLogger("init.install_winget")

def install_winget():
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
        logger.info("bulk install with winget.")
    except subprocess.CalledProcessError as e:
        logger.error(f"winget installation failed: {e}")

