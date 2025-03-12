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


def extract_execution_plan(plan_text) -> list:
    """
    Extracts the execution steps from the given structured plan text.

    Args:
        plan_text (str): The full text containing the plan.

    Returns:
        list: A list of extracted step strings.
    """
    # Define regex pattern to match steps like: "1. Do something"
    step_pattern = re.compile(r"^\d+\.\s+(.+)", re.MULTILINE)

    # Find the Execution Plan section
    execution_plan_match = re.search(r"### Execution Plan:\s*(.*?)\s*(###|$)", plan_text, re.DOTALL)
    
    if not execution_plan_match:
        return []  # Return empty list if no execution plan found

    execution_plan_text = execution_plan_match.group(1)  # Extract just the plan steps section

    # Extract and return all numbered steps as a list
    steps = step_pattern.findall(execution_plan_text)
    return steps


# Main function
async def main() -> None:
    try:
        logger.info("Starting task execution...")
        # tracker.start_recording()

        # -----------------------
        # Agent Planner
        # -----------------------
        agent_planner = init_agent_planner(config, tracker)

        plan = await agent_planner.run(task=config.instruction)
        print(format_autogen_message(plan))
        plan_str = plan.messages[-1].content


        current_plan = plan_str
        while current_plan != 'ALL DONE':

            # Split the plan into array of tasks
            plan_tasks = extract_execution_plan(current_plan)

            # -----------------------
            # Agent ME
            # -----------------------
            agent_me = init_agent_me(
                config, 
                tracker, 
                current_plan
            )

            # Run the task with the team
            stream = agent_me.run_stream(task=plan_tasks[0])

            last_message = None
            async for message in stream:
                last_message = message
                print(format_autogen_message(message))
                
            # -----------------------
            # Agent Summarization - Summarize the actions taken by Agent ME
            # -----------------------
            agent_summarization = init_agent_summarization(
                config, 
                tracker, 
                last_message
            )

            summary = await agent_summarization.run(task=plan_tasks[0])
            print(format_autogen_message(summary))
            summary_str = summary.messages[-1].content

            # -----------------------
            # Agent Replanner
            # -----------------------
            agent_replanner = init_agent_replanner(
                config, 
                tracker, 
                config.instruction, 
                current_plan, 
                summary
            )

            new_plan_response = await agent_replanner.run(task="???? is not used")
            print(format_autogen_message(new_plan_response))
            new_plan = new_plan_response.messages[-1].content

            current_plan = new_plan


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