import os
import sys
import asyncio
import logging
from core.state import State
from core.tracker import Tracker
from core.config import OOConfig
from core.clients.mcp.computer.client import start as start_mcp_client
from functions.executor import FunctionExecutor
from agent_oo1.logging_setup import configure_logging
from agent_oo1.workflow.agent_me import OOAgentMe
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

d = os.path.dirname(__file__)
t = datetime.now().strftime("%Y%m%d_%H%M%S")

# Logging
configure_logging(t)
logger = logging.getLogger("main")

# Tracker object to keep track of images, messages, config and other data
tracker = Tracker(d, t)

# State object to store the current state of the agent
state = State(d, t)

# Configuration object for agent
config = OOConfig()
config.load("teams", "scenario-2")
# tracker.save_config(config)
state.save_config(config)


# Main function
async def start() -> None:
    try:
        logger.info("Starting task execution...")
        # tracker.start_recording()

        await start_mcp_client()

        sys.exit(0)

        # Trigger the start functions
        executor = FunctionExecutor()
        executor.execute_from_list(config.environment.start, state=state)

        # -----------------------
        # Agent ME
        # -----------------------
        agent_me = OOAgentMe(state, tracker)
        _ = await agent_me.run()

        # Trigger the end functions
        executor.execute_from_list(config.environment.end, state=state)

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
