from state import State
from tracker import Tracker
from config import OOConfig
from logging_setup import configure_logging
from workflow.agent_planner import init_agent_planner
from workflow.agent_me import init_agent_me
from workflow.agent_replanner import init_agent_replanner
from environment.computer.env import ComputerEnv
import asyncio
import logging
import sys
import json
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
config = OOConfig()
config.load("teams", "scenario-2")
# tracker.save_config(config)

# Main function
async def main() -> None:
    try:
        logger.info("Starting task execution...")
        # tracker.start_recording()

         # Initialize Windows VM environment
        env = ComputerEnv(config, state, tracker)
        _, _ = env.reset()  

        # -----------------------
        # Agent Planner
        # -----------------------
        agent_planner = init_agent_planner(config, state, tracker)
        _ = await agent_planner.run(task=config.instruction)
        

        # ----------------------
        # ----------------------
        # PLAN LOOP
        # ----------------------
        # ----------------------
        planVersion = 0
        planResult = False

        while planResult == False and planVersion < config.workflow.params.max_plan_versions:
            planVersion += 1

            # -----------------------
            # Agent ME
            # -----------------------
            agent_me = init_agent_me(config, state, tracker, env)
            _ = await agent_me.run()

            sys.exit(0)

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