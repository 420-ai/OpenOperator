import logging
from config import OOConfig
from state import State
from workflow.agent_me.node_get_step import NodeGetStep
from workflow.agent_me.node_is_step_done import NodeIsStepDone
from workflow.agent_me.agent_take_actions import init_agent_take_action
from workflow.agent_me.node_summarize_actions import NodeSummarizeActions
from workflow.agent_me.node_validate_plan_step import NodeValidatePlanStep
from workflow.agent_me.node_is_step_done_by_validation import NodeIsStepDoneByValidation
from workflow.agent_me.node_summarize_plan_step import NodeSummarizePlanStep
from workflow.clients.computer.server_client import get_screenshot
from workflow.helpers import encode_image, format_autogen_message, resize_and_compress_image

logger = logging.getLogger("agent.me")

class OOAgentMe:
    """
    This is the main class for the OOAgentMe agent.
    It handles the initialization and execution
    of the agent's tasks.
    """

    def __init__(self, config: OOConfig, state: State):
        logger.debug("Initializing...")

        self.name = "agent_me"
        self.description = "Agent representing a user controlling computer"

        self.config = config
        self.state = state

        self.nodeGetStep = NodeGetStep(config, state)
        self.nodeIsStepDone = NodeIsStepDone(config, state)
        self.agentTakeActions = None
        self.nodeSummarizeActions = NodeSummarizeActions(config, state)
        self.nodeValidatePlanStep = NodeValidatePlanStep(config, state)
        self.nodeIsStepDoneByValidation = NodeIsStepDoneByValidation(config, state)
        self.nodeSummarizePlanStep = NodeSummarizePlanStep(config, state)

    async def run(self) -> str:

        # Log the current step
        logger.debug("=================================")
        logger.debug(f"Entity: {self.name}")
        logger.debug("=================================")
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

        while planStepValidation == False and planStepIteration < self.config.workflow_settings["max_plan_step_iterations"]:
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

            print("-------------------------")
            print("Plan step:")
            print(task)
            print("-------------------------")

            # We need to reinitialize the agentTakeActions for each iteration
            # because the agent step_counter needs to be reset
            self.agentTakeActions = init_agent_take_action(self.config, self.state)
            stream = self.agentTakeActions.run_stream(task=task)

            print("*" * 20)
            print("Taking actions")
            last_message = None
            async for message in stream:
                last_message = message
                print(format_autogen_message(message))

            print("*" * 20)

            # ----------------------
            # Capture state after action
            # ----------------------
            screenshot_t2 = get_screenshot()
            screenshot_t2_resized = resize_and_compress_image(screenshot_t2)

            # ----------------------
            # Summarize the actions taken
            # ----------------------
            actions_summarization = await self.nodeSummarizeActions.execute(last_message)

            print("-------------------------")
            print("Summarization")
            print(actions_summarization)
            print("-------------------------")

            # ----------------------
            # Validate the plan step
            # ----------------------
            validation = await self.nodeValidatePlanStep.execute(actions_summarization, screenshot_t1_resized, screenshot_t2_resized)

            print("-------------------------")
            print("Validation")
            print(validation)
            print("-------------------------")

            # ----------------------
            # Is the step done?
            # ----------------------
            isStepDone = await self.nodeIsStepDoneByValidation.execute(validation)

            print("-------------------------")
            print("Is the step done?")
            print(isStepDone)
            print("-------------------------")

            planStepValidation = isStepDone == "TRUE"

            print("planStepValidation")
            print(planStepValidation)

            # Save the iteration to the state
            self.state.create_iteration(planStepIteration)
            self.state.save_iteration_actions(actions_summarization)
            self.state.save_validation_result(validation)
            self.state.save_validation_image(screenshot_t1_resized, "t1.png")
            self.state.save_validation_image(screenshot_t2_resized, "t2.png")


        # Save the plan step result to the state
        if planStepValidation == True:
            self.state.save_plan_step_result("Plan step is successfuly done")
        else:
            # Add a summarization of the all actions taken for this plan step
            plan_step_result = f"Plan step reached max iterations of {str(self.config.workflow_settings["max_plan_step_iterations"])}."

            plan_step_summarization = await self.nodeSummarizePlanStep.execute()

            plan_step_result += f" Summarization of what happened: {plan_step_summarization}"
            
            self.state.save_plan_step_result(plan_step_result)

        # ----------------------------------------
        # Perhaps not needed to return any string
        return "Result from Agent ME > AgentReplanner"


def init_agent_me(config: OOConfig, state: State) -> OOAgentMe:
    logger.debug("Initializing agent-me...")

    agent = OOAgentMe(config, state)
    return agent