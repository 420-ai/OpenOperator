import os
import sys
import asyncio
import logging
from core.state import State
from core.tracker import Tracker
from core.config import OOConfig
from agent_oo1.logging_setup import configure_logging
from agent_oo1.workflow.agent_me import OOAgentMe
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

agent_name = os.getenv("AGENT_NAME", "agent_oo1")
print("AGENT_NAME", agent_name)

agent_pvc_path = os.getenv("AGENT_PVC_PATH", os.path.dirname(__file__))
print("AGENT_PVC_PATH", agent_pvc_path)

d = os.path.join(agent_pvc_path, agent_name)
t = datetime.now().strftime("%Y%m%d_%H%M%S")

print("final_dir", d)
print("timestamp", t)

# Logging
configure_logging(t)
logger = logging.getLogger("main")

# Tracker object to keep track of images, messages, config and other data
tracker = Tracker(d, t)

# State object to store the current state of the agent
state = State(d, t)

# Configuration object for agent
config = OOConfig()
config.load("teams", "scenario-0")
# tracker.save_config(config)
state.save_config(config)


# Main function
async def start() -> None:
    try:
        logger.info("Starting task execution...")
        # tracker.start_recording()

        # -----------------------
        # Agent ME
        # -----------------------
        agent_me = OOAgentMe(state, tracker)
        _ = await agent_me.run()

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.exception(e)

    except asyncio.CancelledError:
        logger.warning("Task was cancelled.")

    # finally:
    #     logger.info("Stopping recording and saving the file...")
    #     tracker.end_recording()


if __name__ == "__main__":
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Cleaning up before exit...")
