import logging
from config import OOConfig
from state import State
from agent.agent_me.node_get_step import NodeGetStep
from agent.agent_me.node_is_step_done import NodeIsStepDone
from agent.agent_me.agent_take_actions import init_agent_take_action
from agent.agent_me.node_summarize_actions import NodeSummarizeActions
from agent.agent_me.node_validate_plan_step import NodeValidatePlanStep
from agent.clients.computer.server_client import get_screenshot
from agent.helpers import encode_image, format_autogen_message, resize_and_compress_image

logger = logging.getLogger("agent.me")

class OOAgentMe:
    """
    This is the main class for the OOAgentMe agent.
    It handles the initialization and execution
    of the agent's tasks.
    """

    def __init__(self, config: OOConfig, state: State):
        logger.debug("Initializing...")
        self.config = config
        self.state = state

        self.nodeGetStep = NodeGetStep(config, state)
        self.nodeIsStepDone = NodeIsStepDone(config, state)
        self.nodeTakeActions = init_agent_take_action(config, state)
        self.nodeSummarizeActions = NodeSummarizeActions(config, state)
        self.nodeValidatePlanStep = NodeValidatePlanStep(config, state)

    async def run(self) -> str:
        logger.debug("Running...")
        
        # ----------------------
        # Get the first step of the plan
        # ----------------------
        await self.nodeGetStep.execute()

        # ----------------------
        # Is the step done?
        # ----------------------
        isDone = await self.nodeIsStepDone.execute()
        
        print("-------------------------")
        print("Is the step done?")
        print(isDone)
        print("-------------------------")

        if isDone == "TRUE":
            return "AgenMe is done with the step, because it is already done"
        

        # ----------------------
        # ----------------------
        # PLAN STEP LOOP
        # ----------------------
        # ----------------------
        planStepValidation = False
        planStepIteration = 0

        while planStepValidation == False & planStepIteration < self.config.workflow_settings.max_plan_step_iterations:
            planStepIteration += 1

            # ----------------------
            # Capture state before action
            # ----------------------
            screenshot_t1 = get_screenshot()
            screenshot_t1_resized = resize_and_compress_image(screenshot_t1)

            # ----------------------
            # Take actions
            # ----------------------
            task = self.state.current_plan_data["plan_step"]["text"]

            stream = self.nodeTakeActions.run_stream(task=task)

            print("-------------------------")
            print("Taking actions")
            last_message = None
            async for message in stream:
                last_message = message
                print(format_autogen_message(message))

            print("-------------------------")

            # ----------------------
            # Capture state after action
            # ----------------------
            screenshot_t2 = get_screenshot()
            screenshot_t2_resized = resize_and_compress_image(screenshot_t2)



            # ----------------------
            # Summarize the actions taken
            # ----------------------
            summarization = await self.nodeSummarizeActions.execute(last_message)

            print("-------------------------")
            print("Summarization")
            print(summarization)
            print("-------------------------")

            # ----------------------
            # Validate the plan step
            # ----------------------
            validation = self.nodeValidatePlanStep.execute(summarization, screenshot_t1_resized, screenshot_t2_resized)

            print("-------------------------")
            print("Validation")
            print(validation)
            print("-------------------------")

        # Perhpaps not needed
        return "DUMMY result from Agent ME"


def init_agent_me(config: OOConfig, state: State) -> OOAgentMe:
    logger.debug("Initializing agent-me...")

    agent = OOAgentMe(config, state)
    return agent