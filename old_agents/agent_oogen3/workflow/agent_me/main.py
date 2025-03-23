import logging
from config import OOConfig
from state import State
from tracker import Tracker
from workflow.agent_me.node_get_step import NodeGetStep
from workflow.agent_me.node_is_step_done import NodeIsStepDone
from workflow.agent_me.agent_computer import init_agent_computer
from workflow.agent_me.node_summarize_actions import NodeSummarizeActions
from workflow.agent_me.node_validate_plan_step import NodeValidatePlanStep
from workflow.agent_me.node_is_step_done_by_validation import NodeIsStepDoneByValidation
from workflow.agent_me.node_summarize_plan_step import NodeSummarizePlanStep
from workflow.clients.computer import ComputerClient
from helpers import encode_image, format_autogen_message, resize_and_compress_image

logger = logging.getLogger("agent_me")

class OOAgentMe:
    """
    This is the main class for the OOAgentMe agent.
    It handles the initialization and execution
    of the agent's tasks.
    """

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_me"
        self.description = "Agent representing a user controlling computer"

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.computer = ComputerClient(server_url=f"{self.config.environment.params.server_ip}:{self.config.environment.params.computer_port}")

        self.nodeGetStep = NodeGetStep(state, tracker)
        self.nodeIsStepDone = NodeIsStepDone(state, tracker)
        self.agentComputer = None
        self.nodeSummarizeActions = NodeSummarizeActions(state, tracker)
        self.nodeValidatePlanStep = NodeValidatePlanStep(state, tracker)
        self.nodeIsStepDoneByValidation = NodeIsStepDoneByValidation(state, tracker)
        self.nodeSummarizePlanStep = NodeSummarizePlanStep(state, tracker)

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
        if isDone == True:
            return "AgenMe is done with the step, because it is already done"


        # ----------------------
        # ----------------------
        # PLAN STEP LOOP
        # ----------------------
        # ----------------------
        planStepValidation = False
        planStepIteration = 0

        while planStepValidation == False and planStepIteration < self.config.workflow.params.max_plan_step_iterations:
            planStepIteration += 1

            logger.debug("--------------------------")
            logger.debug(f"Plan step iteration: {planStepIteration}")
            logger.debug("--------------------------")
            self.state.create_iteration(planStepIteration)

            # ----------------------
            # Capture state before action
            # ----------------------
            screenshot_t1 = self.computer.get_screenshot()
            screenshot_t1_resized = resize_and_compress_image(screenshot_t1)

            # region Log + State + Tracker
            self.state.save_plan_image(screenshot_t1, "t1.png")
            self.state.save_plan_image(screenshot_t1_resized, "t1_resized.png")
            self.state.save_iteration_validation_image(screenshot_t1_resized, "t1.png")

            self.tracker.save(self.name, [
                ("screenshot_t1_resized", screenshot_t1_resized),
            ])
            # endregion

            # ----------------------
            # ----------------------
            # Agent computer
            # ----------------------
            # ----------------------
            task = self.state.current_plan_data["plan_step"]["text"]

            # We need to reinitialize the agentTakeActions for each iteration
            # because the agent step_counter needs to be reset
            self.agentComputer = init_agent_computer(self.state, self.tracker)
            stream = self.agentComputer.run_stream(task=task)

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
            screenshot_t2 = self.computer.get_screenshot()
            screenshot_t2_resized = resize_and_compress_image(screenshot_t2)

            # region Log + State + Tracker
            self.state.save_plan_image(screenshot_t2, "t2.png")
            self.state.save_plan_image(screenshot_t2_resized, "t2_resized.png")
            self.state.save_iteration_validation_image(screenshot_t2_resized, "t2.png")

            self.tracker.save(self.name, [
                ("screenshot_t2_resized", screenshot_t2_resized),
            ])
            # endregion

            # ----------------------
            # Summarize the actions taken
            # ----------------------
            actions_summarization = await self.nodeSummarizeActions.execute(last_message)
            self.state.save_iteration_actions(actions_summarization)

            # ----------------------
            # Validate the plan step
            # ----------------------
            validation = await self.nodeValidatePlanStep.execute(actions_summarization)
            self.state.save_iteration_validation_result(validation)

            # ----------------------
            # Is the step done?
            # ----------------------
            planStepValidation = await self.nodeIsStepDoneByValidation.execute(validation)


        # Save the plan step result to the state
        if planStepValidation == True:
            plan_step_result = f"Plan step is successfuly done after {str(planStepIteration)} iterations."

            # region Log + State + Tracker
            logger.debug(plan_step_result)

            self.state.save_plan_step_result(plan_step_result)

            self.tracker.save(self.name, [
                ("plan_step_result", plan_step_result),
            ])
            # endregion
        else:
            # Add a summarization of the all actions taken for this plan step
            plan_step_result = f"Plan step reached max iterations of {str(self.config.workflow.params.max_plan_step_iterations)}."

            plan_step_summarization = await self.nodeSummarizePlanStep.execute()

            plan_step_result += f" Summarization of what happened: {plan_step_summarization}"
            
            # region Log + State + Tracker
            logger.debug(plan_step_result)

            self.state.save_plan_step_result(plan_step_result)

            self.tracker.save(self.name, [
                ("plan_step_result", plan_step_result),
            ])
            # endregion

        # ----------------------------------------
        # Perhaps not needed to return any string
        return "Agent ME > AgentReplanner"


def init_agent_me(state: State, tracker: Tracker) -> OOAgentMe:
    logger.debug("Initializing agent-me...")
    return OOAgentMe(state, tracker)