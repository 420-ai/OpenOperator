from state import State
from tracker import Tracker
from config import OOConfig
from logging_setup import configure_logging
from workflow.agent_planner import init_agent_planner
from workflow.agent_me import init_agent_me
from workflow.agent_replanner import init_agent_replanner
from workflow.helpers import format_autogen_message
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
        agent_planner = init_agent_planner(config, state)

        plan = await agent_planner.run(task=config.instruction)
        print(format_autogen_message(plan))
        plan_str = plan.messages[-1].content

        # ----------------------
        # ----------------------
        # PLAN LOOP
        # ----------------------
        # ----------------------
        planVersion = 0
        planResult = False

        while planResult == False and planVersion < config.workflow_settings["max_plan_versions"]:
            planVersion += 1

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
            agent_replanner = init_agent_replanner(config, state)
            result = await agent_replanner.run()
            print("Agent Replanner result:")
            print(result)
            
            if result == "ALL DONE":
                planResult = True
                break


        # Save the plan step result to the state
        if planResult == True:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("PLAN FINISHED SUCCESSFULLY")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        else:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("PLAN REACHED MAX VERSIONS")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        logger.info("PLAN LOOP END")


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