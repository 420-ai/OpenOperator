import os
import shutil
import subprocess

import logging
logger = logging.getLogger("init.verify_node_npm")

def verify_node_and_npm():
    node_path = shutil.which("node") or r"C:\Program Files\nodejs\node.exe"
    npm_path = shutil.which("npm") or r"C:\Program Files\nodejs\npm.cmd"

    logger.info(f"Checking Node.js at: {node_path}")
    logger.info(f"Checking npm at: {npm_path}")

    if not os.path.exists(node_path):
        logger.error("Node.js not found. Make sure it is installed and PATH is refreshed.")
        return False

    if not os.path.exists(npm_path):
        logger.error("npm not found. Make sure it is installed and PATH is refreshed.")
        return False

    try:
        subprocess.run([node_path, "--version"], check=True)
        subprocess.run([npm_path, "--version"], check=True)
        logger.info("Node.js and npm are available.")
        return True
    except Exception as e:
        logger.error(f"Error verifying Node/npm: {e}")
        return False
