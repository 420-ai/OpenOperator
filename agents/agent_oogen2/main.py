from autogen_agentchat.ui import Console
import asyncio
from agent.agent_planner import OOPlannerAgent
from agent.agent_me import OOMeAgent
from agent.agent_me2 import agent
from agent.team import team
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
        "level": "INFO",
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
        "openai": {  
            "level": "INFO",
            "propagate": False,
        },
        "httpcore": {
            "level": "INFO",
            "propagate": False,
        },
        "autogen_core": {
            "level": "ERROR",
            "propagate": False,
        },
        "httpx": {
            "level": "ERROR",
            "propagate": False,
        },
        "autogen_agentchat": {
            "level": "ERROR",
            "propagate": False,
        },
        "asyncio": {
            "level": "ERROR",
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

    # agent_planner = OOPlannerAgent()
    # agent_me = OOMeAgent()

    stream = team.run_stream(task=TASK)
    await Console(stream)

    # Message as string
    # result = await team.run(task=TASK)
    # print(result.messages[len(result.messages) - 1].content)

asyncio.run(main())