import logging
from config import OOConfig
from state import State
from workflow.agent_replanner.node_summarize_plan_versions import NodeSummarizeAllPlanVersions
from workflow.agent_replanner.node_replan import NodeReplan
from workflow.clients.computer.server_client import get_screenshot
from workflow.helpers import encode_image, format_autogen_message, resize_and_compress_image

logger = logging.getLogger("agent.replanner")

class OOAgentReplanner:
    """
    This is the main class for the OOAgentReplanner agent.
    It handler reviewing the plan step and replanning if needed.
    """

    def __init__(self, config: OOConfig, state: State):
        logger.debug("Initializing...")

        self.name = "agent_replanner"
        self.description = "Agent responsible for replanning"

        self.config = config
        self.state = state

        self.nodeSummarizeAllPlanVersions = NodeSummarizeAllPlanVersions(config, state)
        self.nodeReplan = NodeReplan(config, state)

    async def run(self) -> str:

        # Log the current step
        logger.debug("=================================")
        logger.debug(f"Entity: {self.name}")
        logger.debug("=================================")
        logger.debug("Running...")

        # Take a screenshot of the current UI state
        screenshot = get_screenshot()
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


def init_agent_replanner(config: OOConfig, state: State) -> OOAgentReplanner:
    logger.debug("Initializing agent-replanner...")

    agent = OOAgentReplanner(config, state)
    return agent