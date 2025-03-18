from config import OOConfig
from state import State
from tracker import Tracker
from workflow.agent_replanner.node_summarize_plan_versions import NodeSummarizeAllPlanVersions
from workflow.agent_replanner.node_replan import NodeReplan
from clients.computer import computer
from helpers import resize_and_compress_image

import logging
logger = logging.getLogger("agent_replanner")

class OOAgentReplanner:
    """
    This is the main class for the OOAgentReplanner agent.
    It handler reviewing the plan step and replanning if needed.
    """

    def __init__(self, config: OOConfig, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_replanner"
        self.description = "Agent responsible for replanning"

        self.config = config
        self.state = state
        self.tracker = tracker

        self.computer = computer

        self.nodeSummarizeAllPlanVersions = NodeSummarizeAllPlanVersions(config, state, tracker)
        self.nodeReplan = NodeReplan(config, state, tracker)

    async def run(self) -> str:

        # Log the current step
        logger.debug("=================================")
        logger.debug(f"Entity: {self.name}")
        logger.debug("=================================")
        logger.debug("Running...")

        # Take a screenshot of the current UI state
        screenshot = computer.get_screenshot()
        # Resize and compress the screenshot
        screenshot_resized = resize_and_compress_image(screenshot)
        # Save into state
        self.state.save_plan_image(screenshot_resized, "t3.png")
        
        # ----------------------
        # Summarize all plan versions
        # ----------------------
        summarization = await self.nodeSummarizeAllPlanVersions.execute()

        print("-------------------------")
        print("Summarization of all plan versions:")
        print(summarization)
        print("-------------------------")

        # ----------------------
        # Replan
        # ----------------------
        result = await self.nodeReplan.execute(history=summarization)


        # ----------------------
        # Create a new plan version, if the plan is not done
        # ----------------------
        if result != "ALL DONE":
            # Create a new plan version
            self.state.create_new_plan_version()
            self.state.save_plan_text(result)
            self.state.save_plan_image(screenshot_resized, "t0.png")

        return result


def init_agent_replanner(config: OOConfig, state: State, tracker: Tracker) -> OOAgentReplanner:
    logger.debug("Initializing agent-replanner...")
    return OOAgentReplanner(config, state, tracker)