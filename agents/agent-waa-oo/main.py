import os
import json
import shutil
import traceback
import logging
import json
import logging.config
import os
import traceback
from dotenv import load_dotenv
load_dotenv()

from agent.main import OOAgent
from environment.computer.env import ComputerEnv
from run import run

# print("Environment variables")
# print(os.getenv("AZURE_API_KEY"))
# print(os.getenv("AZURE_ENDPOINT"))


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
# Parameters
logger.info("Setting up parameters...")

model="gpt-4o"
temparature=1

emulator_ip = "127.0.0.1" # Server2 on computer ["windows VM in docker" or "windows VM"]
emulator_port = 5050 # Server2 on computer ["windows VM in docker" or "windows VM"]

max_steps = 15
scores = []

config_base_dir = "configs"
results_base_dir = "results"
domain = "notepad"
config_id = "366de66e-cbae-4d72-b042-26390db2b145-WOS"

# -------------------------------------------------------

config_file_path = os.path.join(CURRENT_FOLDER, config_base_dir, domain, f"{config_id}.json")
with open(config_file_path, "r", encoding="utf-8") as f:
    config_file = json.load(f)

result_path = os.path.join(CURRENT_FOLDER, results_base_dir, domain, config_id)
if os.path.exists(result_path):
    shutil.rmtree(result_path)
os.makedirs(result_path, exist_ok=True)
# -------------------------------------------------------
# -------------------------------------------------------
# Objects
logger.info("Setting up objects...")

# TODO:
# Optimize the action_space !!

agent = OOAgent(
            model=model,
            temperature=temparature
        )

env = ComputerEnv(
        action_space=agent.action_space,
        emulator_ip=emulator_ip, 
        emulator_port=emulator_port, 
    )

# -------------------------------------------------------
# -------------------------------------------------------
# -------------------------------------------------------
# Run agent
logger.info(f"Running {domain}/{config_id} ...")

try:
    run(
        agent, 
        env, 
        config_file, 
        max_steps, 
        result_path,
        scores
    )
except Exception as e:
    logger.error(f"Exception in {domain}/{config_id}: {e}")
    error_traceback = traceback.format_exc()
    logger.error(error_traceback)
else:
    logger.info(f"Finished {domain}/{config_id} with scores: {scores}")
finally:
    env.close()
