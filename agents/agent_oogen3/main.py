from state import State
from tracker import Tracker
from config import config
from logging_setup import configure_logging
from workflow.agent_planner import init_agent_planner
from workflow.agent_me import init_agent_me
from workflow.agent_replanner import init_agent_replanner
from workflow.node_summarize import OONodeSummarize
import asyncio
import logging
import re
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

        # -----------------------
        # Agent Planner
        # -----------------------
        agent_planner = init_agent_planner(state, tracker)
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
            agent_me = init_agent_me(state, tracker)
            _ = await agent_me.run()

            # -----------------------
            # Agent Replanner
            # -----------------------
            agent_replanner = init_agent_replanner(state, tracker)
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
        summarization = node_summarize.execute()

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