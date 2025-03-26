import sys
import asyncio
import logging
from core.state import State
from core.tracker import Tracker
from core.config import OOConfig
from functions.executor import FunctionExecutor
from agent_oo4.logging_setup import configure_logging
from agent_oo4.workflow.agent_planner import OOPlannerAgent
from agent_oo4.workflow.agent_me import OOAgentMe
from agent_oo4.workflow.agent_replanner import OOAgentReplanner
from agent_oo4.workflow.node_summarize import OONodeSummarize
from agent_oo4.environment.computer.env import ComputerEnv
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
import os

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
        executor.execute_from_list(config.environment.start, state=state)

         # Initialize Windows VM environment
        env = ComputerEnv(state, tracker)
        _, _ = env.reset()  

        # -----------------------
        # Agent Planner
        # -----------------------
        agent_planner = OOPlannerAgent(state, tracker)
        _ = await agent_planner.run()

        # ----------------------
        # ----------------------
        # PLAN LOOP
        # ----------------------
        # ----------------------
        planVersion = 0
        planResult = False

        while planResult == False and planVersion < config.workflow.params.max_plan_versions:
            planVersion += 1

            logger.debug("--------------------------")
            logger.debug(f"Workflow - Plan version: {planVersion}")
            logger.debug("--------------------------")

            # -----------------------
            # Agent ME
            # -----------------------
            agent_me = OOAgentMe(state, tracker, env)
            _ = await agent_me.run()

            # -----------------------
            # Agent Replanner
            # -----------------------
            agent_replanner = OOAgentReplanner(state, tracker)
            result = await agent_replanner.run()
            
            if result == "ALL DONE":
                planResult = True
                break

            if "all done" in result.lower():
                raise ValueError("Agent Replanner returned 'ALL DONE' in the text, but not only 'ALL DONE' ------> INVESTIGATE")

        # -----------------------
        # Node Summarization
        # -----------------------
        node_summarize = OONodeSummarize(state, tracker)
        summarization = await node_summarize.execute()

        # Save the plan step result to the state
        task_result = ""
        if planResult == True:
            task_result = f"""Task completed successfully.
            
            Here is the summarization of the steps taken:
            =============================================
            {summarization}
            =============================================
            """
        else:
            task_result = f"""Task reached maximum plan versions of {config.workflow.params.max_plan_versions}.
            
            Here is the summarization of the steps taken:
            =============================================
            {summarization}
            =============================================
            """

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