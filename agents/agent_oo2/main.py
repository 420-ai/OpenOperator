import os
import sys
import asyncio
import logging
from core.state import State
from core.tracker import Tracker
from core.config import OOConfig
from functions.executor import FunctionExecutor
from agent_oo2.logging_setup import configure_logging
from agent_oo2.workflow.agent_me.main import OOAgentMe
from agent_oo2.workflow.node_planner import OOPlannerNode
from agent_oo2.workflow.node_replanner import OOReplannerNode
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

        # Trigger the start functions
        executor = FunctionExecutor()
        executor.execute_from_list(config.environment.start)

        # -----------------------
        # Planner Node
        # -----------------------
        node_planner = OOPlannerNode(state, tracker)
        _ = await node_planner.execute()

        # ----------------------
        # ----------------------
        # PLAN LOOP
        # ----------------------
        # ----------------------
        planVersion = -1
        planResult = False

        while planResult == False and planVersion < config.workflow.params.max_plan_versions:
            planVersion += 1
            
            logger.debug("--------------------------")
            logger.debug(f"Workflow - Plan version: {planVersion}")
            logger.debug("--------------------------")

            # -----------------------
            # Agent ME
            # -----------------------
            agent_me = OOAgentMe(state, tracker)
            _ = await agent_me.run()

            # -----------------------
            # RePlanner Node
            # -----------------------
            node_replanner = OOReplannerNode(state, tracker)
            result = await node_replanner.execute()

            if result == "ALL DONE":
                planResult = True
                break

            if "all done" in result.lower():
                raise ValueError("Agent Replanner returned 'ALL DONE' in the text, but not only 'ALL DONE' ------> INVESTIGATE")


        # Save the plan step result to the state
        task_result = ""
        if planResult == True:
            task_result = f"""Task completed successfully."""
        else:
            task_result = f"""Task reached maximum plan versions of {config.workflow.params.max_plan_versions}."""

        # region Log + State + Tracker
        logger.info("----------------------------")
        logger.info(task_result)
        logger.info("----------------------------")

        state.save_task_result(task_result)

        tracker.save("main", [
            ("task_result", task_result),
        ])
        # endregion

        # Trigger the end functions
        executor.execute_from_list(config.environment.end)

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