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
        agent_planner = init_agent_planner(config, tracker)

        plan = await agent_planner.run(task=config.instruction)
        print(format_autogen_message(plan))
        plan_str = plan.messages[-1].content


        current_plan = plan_str
        while current_plan != 'ALL DONE':

            # Split the plan into array of tasks
            plan_tasks = extract_plan_steps(current_plan)
            plan_tasks_arr = plan_tasks.split("\n")

            # -----------------------
            # Agent ME
            # -----------------------
            agent_me = init_agent_me(
                config, 
                tracker, 
                current_plan
            )

            # Run the task with the team
            stream = agent_me.run_stream(task=plan_tasks_arr[0])

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

            summary = await agent_summarization.run(task=plan_tasks_arr[0])
            print(format_autogen_message(summary))

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