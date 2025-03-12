from state import State
from tracker import Tracker
from config import OOConfig
from logging_setup import configure_logging
from agent.agent_planner import init_agent_planner
from agent.agent_me import init_agent_me
from agent.agent_replanner import init_agent_replanner
from agent.agent_summarization import init_agent_summarization
from agent.helpers import format_autogen_message
import asyncio
import logging
import re
logger = logging.getLogger("main")

# Tracker object to log images, messages, config and other data
tracker = Tracker()
configure_logging(tracker.result_dir)

# Configuration object for agent
config = OOConfig()
config.load("teams", "scenario-2")
tracker.save_config(config)

state = State()

# Main function
async def main() -> None:
    try:
        logger.info("Starting task execution...")
        # tracker.start_recording()

        # -----------------------
        # Agent Planner
        # -----------------------
        agent_planner = init_agent_planner(config, tracker, state)

        plan = await agent_planner.run(task=config.instruction)
        print(format_autogen_message(plan))
        plan_str = plan.messages[-1].content


        # -----------------------
        # Agent ME
        # -----------------------
        agent_me = init_agent_me(config, state)
        result = await agent_me.run()
        print("Agent ME result:")
        print(result)


        # -----------------------
        # Agent Replanner
        # -----------------------
        # TBD


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