import asyncio
import logging
from tracker import Tracker
from config import config
from state import State
from logging_setup import configure_logging
from workflow.agent_me import init_agent_me
from helpers import format_autogen_message

from datetime import datetime
t = datetime.now().strftime("%Y%m%d_%H%M%S")

# Logging
configure_logging(t)
logger = logging.getLogger("main")

# Tracker object to keep track of images, messages, config and other data
tracker = Tracker(t)

# State object to store the current state of the agent
state = State(t)

# Configuration object for agent
# config = OOConfig()
config.load("teams", "scenario-2")
# tracker.save_config(config)
state.save_config(config)

# Main function
async def main() -> None:
    try:
        logger.info("Starting task execution...")
        # tracker.start_recording()
        state.create_new_plan_version()

        agent = init_agent_me(state, tracker)

        # Run the task with the team
        stream = agent.run_stream(task=config.instruction)

        async for message in stream:
            logger.debug(format_autogen_message(message))
                
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
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Cleaning up before exit...")