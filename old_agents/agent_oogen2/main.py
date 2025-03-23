from tracker import Tracker
from config import config
from state import State

from logging_setup import configure_logging
from workflow.agent_planner import init_agent_planner
from workflow.agent_me import init_agent_me
from workflow.agent_replanner import init_agent_replanner
from workflow.agent_summarization import init_agent_summarization
from helpers import format_autogen_message
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



def extract_plan_steps(text):
    """
    Extracts only the numbered plan steps from the given text formatted with Visual Description and Action sections.
    """
    match = re.search(r"### Action:\s+\*\*Plan\*\*:\s+(.*)", text, re.DOTALL)  # Find the Plan section
    if match:
        plan_text = match.group(1).strip()
        steps = re.findall(r"\d+\.\s.*", plan_text)  # Extract only numbered steps
        return "\n".join(steps)
    return ""

# Main function
async def main() -> None:
    try:
        logger.info("Starting task execution...")
        # tracker.start_recording()

        # -----------------------
        # Agent Planner
        # -----------------------
        agent_planner = init_agent_planner(state, tracker)
        plan = await agent_planner.run(task=config.instruction)

        current_plan = plan.messages[-1].content

        # ----------------------
        # ----------------------
        # PLAN LOOP
        # ----------------------
        # ----------------------
        planVersion = 0
        planResult = False

        while planResult == False and planVersion < config.workflow.params.max_plan_versions:
            planVersion += 1

            # Split the plan into array of tasks
            plan_tasks = extract_plan_steps(current_plan)
            plan_tasks_arr = plan_tasks.split("\n")

            # -----------------------
            # Agent ME
            # -----------------------
            agent_me = init_agent_me(
                state, 
                tracker, 
                current_plan
            )

            # Run the task with the team
            stream = agent_me.run_stream(task=plan_tasks_arr[0])

            last_message = None
            async for message in stream:
                last_message = message
                logger.debug(format_autogen_message(message))
                
            # -----------------------
            # Agent Summarization - Summarize the actions taken by Agent ME
            # -----------------------
            agent_summarization = init_agent_summarization(
                state, 
                tracker, 
                last_message
            )

            summary = await agent_summarization.run(task=plan_tasks_arr[0])
            logger.debug(format_autogen_message(summary))

            # -----------------------
            # Agent Replanner
            # -----------------------
            agent_replanner = init_agent_replanner(
                state, 
                tracker, 
                config.instruction, 
                current_plan, 
                summary
            )

            new_plan_response = await agent_replanner.run(task="???? is not used")
            new_plan = new_plan_response.messages[-1].content

            current_plan = new_plan

            if "all done" in current_plan.lower():
                raise ValueError("Agent Replanner returned 'ALL DONE' in the text, but not only 'ALL DONE' ------> INVESTIGATE")

            if current_plan == "ALL DONE":
                planResult = True
                break
            elif current_plan != "ALL DONE":
                screenshot_t0 = state.get_current_plan_image("t2")
                # Create a new plan version
                state.create_new_plan_version()
                state.save_plan_text(current_plan)
                state.save_plan_image(screenshot_t0, "t0.png")


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