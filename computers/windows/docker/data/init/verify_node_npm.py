import os
import shutil
import subprocess

from utils import update_path_globally_and_temporarily

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

    # Add only directories to PATH
    update_path_globally_and_temporarily(os.path.dirname(node_path))
    update_path_globally_and_temporarily(os.path.dirname(npm_path))

    # Node.js ----------------
    print("node in PATH?", shutil.which("node"))

    try:
        subprocess.run(["node", "--version"], check=True)
        logger.info("Node.js is available.")     
    except Exception as e:
        logger.error(f"Error verifying Node: {e}")
        return False


    # NPM ----------------
    print("npm in PATH?", shutil.which("npm"))

    try:
        subprocess.run(["npm", "--version"], shell=True, check=True)
        logger.info("NPM is available.")  
    except FileNotFoundError as e:
        logger.error(f"Error verifying NPM: {e}")
        return False

    return True
