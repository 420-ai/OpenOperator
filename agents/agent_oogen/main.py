from tracker import Tracker
from config import OOConfig
from logging_setup import configure_logging
from autogen_agentchat.ui import Console
from agent.team import init_team
import asyncio
import logging
logger = logging.getLogger("main")

# Tracker object to log images, messages, config and other data
tracker = Tracker()
configure_logging(tracker.result_dir)

# Configuration object for agent
config = OOConfig()
config.load("teams", "scenario-2")
tracker.save_config(config)

# Main function
async def main() -> None:
    try:
        team = init_team(config, tracker)

        logger.info("Starting task execution...")
        tracker.start_recording()

        # Run the task with the team
        stream = team.run_stream(task=config.instruction)
        await Console(stream)

        while True:
            # Get user input from the console.
            user_input = input("Enter a message (type 'exit' to leave): ")
            if user_input.strip().lower() == "exit":
                break
            # Run the team and stream messages to the console.
            stream = team.run_stream(task=user_input)
            await Console(stream)

    except asyncio.CancelledError:
        logger.warning("Task was cancelled.")
    
    finally:
        logger.info("Stopping recording and saving the file...")
        tracker.end_recording()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Cleaning up before exit...")