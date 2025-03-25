from core.clients.computer import ComputerClient
from core.state import State
from core.tracker import Tracker
from agent_oo4.workflow.agent_replanner.node_format_plan_versions import NodeFormatAllPlanVersions
from agent_oo4.workflow.agent_replanner.node_replan import NodeReplan
from agent_oo4.helpers import resize_and_compress_image

import logging
logger = logging.getLogger("agent_replanner")

class OOAgentReplanner:
    """
    This is the main class for the OOAgentReplanner agent.
    It handler reviewing the plan step and replanning if needed.
    """

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_replanner"
        self.description = "Agent responsible for replanning"

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.computer = ComputerClient()

        self.nodeFormatAllPlanVersions = NodeFormatAllPlanVersions(state, tracker)
        self.nodeReplan = NodeReplan(state, tracker)

    async def run(self) -> str:

        # Log the current step
        logger.debug("=================================")
        logger.debug(f"Entity: {self.name}")
        logger.debug("=================================")
        logger.debug("Running...")

        # Take a screenshot of the current UI state
        screenshot = self.computer.get_screenshot()
        # Resize and compress the screenshot
        screenshot_resized = resize_and_compress_image(screenshot)

        self.state.save_plan_image(screenshot_resized, "t3.png")
        
        # ----------------------
        # Format all plan versions
        # ----------------------
        formatted_all_plan_versions = await self.nodeFormatAllPlanVersions.execute()

        # ----------------------
        # Replan
        # ----------------------
        result = await self.nodeReplan.execute(history=formatted_all_plan_versions)

        # ----------------------
        # Create a new plan version, if the plan is not done
        # ----------------------
        if result != "ALL DONE":
            # Create a new plan version
            self.state.create_new_plan_version()
            self.state.save_plan_text(result)
            self.state.save_plan_image(screenshot_resized, "t0.png")

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("new_plan", result),
            ("screenshot_t3_resized", screenshot_resized),
        ])
        # endregion

        return result
