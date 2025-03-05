from autogen_agentchat.ui import Console
import asyncio
from agent.main import OOGenAgent
import logging.config
import os

CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
# -------------------------------------------------------
# -------------------------------------------------------
# Logging

LOG_DIR = os.path.join(CURRENT_FOLDER, "logs")
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure the directory exists
LOG_FILE = os.path.join(LOG_DIR, "app.log")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": LOG_FILE,
            "formatter": "detailed",
            "level": "DEBUG",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "detailed",
            "level": "DEBUG",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
    "loggers": {
        "urllib3": {  
            "level": "INFO",
            "propagate": False,
        },
        "PIL": {  
            "level": "INFO",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("main")

# -------------------------------------------------------
# -------------------------------------------------------

TASK = 'Please open Notepad, create a new file named "draft.txt", type "This is a draft.", and save it to the Documents folder.'

# Main function
async def main() -> None:

    agent = OOGenAgent()

    stream = agent.run_stream(task=TASK)
    await Console(stream)

asyncio.run(main())