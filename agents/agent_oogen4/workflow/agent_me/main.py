import sys
from config import OOConfig
from state import State
from tracker import Tracker
from helpers import resize_and_compress_image
from workflow.agent_me.node_get_step import NodeGetStep
from workflow.agent_me.node_is_step_done import NodeIsStepDone
from workflow.agent_me.node_summarize_actions import NodeSummarizeActions
from workflow.agent_me.node_validate_plan_step import NodeValidatePlanStep
from workflow.agent_me.node_is_step_done_by_validation import NodeIsStepDoneByValidation
from workflow.agent_me.node_summarize_plan_step import NodeSummarizePlanStep
from clients.computer import computer
from environment.computer.env import ComputerEnv

import logging
logger = logging.getLogger("agent_me")

class OOAgentMe:
    """
    This is the main class for the OOAgentMe agent.
    It handles the initialization and execution
    of the agent's tasks.
    """

    def __init__(self, config: OOConfig, state: State, tracker: Tracker, env: ComputerEnv):
        logger.debug("Initializing...")

        self.name = "agent_me"
        self.description = "Agent representing a user controlling computer"

        self.config = config
        self.state = state
        self.tracker = tracker  

        self.computer = computer
        self.computerEnv = env

        self.nodeGetStep = NodeGetStep(config, state, tracker)
        self.nodeIsStepDone = NodeIsStepDone(config, state, tracker)
        self.agentComputer = None
        self.nodeSummarizeActions = NodeSummarizeActions(config, state, tracker)
        self.nodeValidatePlanStep = NodeValidatePlanStep(config, state, tracker)
        self.nodeIsStepDoneByValidation = NodeIsStepDoneByValidation(config, state, tracker)
        self.nodeSummarizePlanStep = NodeSummarizePlanStep(config, state, tracker)

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

            # ----------------------
            # Capture state before action
            # ----------------------
            screenshot_t1 = self.computer.get_screenshot()
            screenshot_t1_resized = resize_and_compress_image(screenshot_t1)

            # ----------------------
            # Convert the plan step to an actions
            # ----------------------
            task = self.state.current_plan_data["plan_step"]["text"]

            # region Log + State + Tracker
            logger.debug(f"Plan step: {task}")

            self.tracker.save(self.name, [
                ("screenshot_t1_resized", screenshot_t1_resized),
                ("plan_step", task)
            ])
            # endregion

            # LK TODO:
            # FINISH DESIGN THE LLM CALL 
            # FOR CONVERTING THE PLAN STEP TO ACTIONS


            sys.exit(0)
            # ----------------------
            # Take actions in the environment
            # ----------------------

            # Parse Action from Plan
            # action_type, element_id = parse_task_to_action(task, observation["ui_elements"])
            # if action_type is not None and element_id is not None:
            #     obs, reward, done, _ = self.computerEnv.step((action_type, element_id))
            #     print(f"Action {action_type} on UI element {element_id}: Reward = {reward}")
            
            # ----------------------
            # Capture state after action
            # ----------------------
            screenshot_t2 = self.computer.get_screenshot()
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

            # Save the iteration to the state
            self.state.create_iteration(planStepIteration)
            self.state.save_iteration_actions(actions_summarization)
            self.state.save_iteration_validation_result(validation)
            self.state.save_iteration_validation_image(screenshot_t1_resized, "t1.png")
            self.state.save_iteration_validation_image(screenshot_t2_resized, "t2.png")


        # Save the plan step result to the state
        if isStepDone == True:
            self.state.save_plan_step_result("Plan step is successfuly done")
        else:
            # Add a summarization of the all actions taken for this plan step
            plan_step_result = f"Plan step reached max iterations of {str(self.config.workflow["max_plan_step_iterations"])}."

            plan_step_summarization = await self.nodeSummarizePlanStep.execute()

            plan_step_result += f" Summarization of what happened: {plan_step_summarization}"
            
            self.state.save_plan_step_result(plan_step_result)

        # ----------------------------------------
        # Perhaps not needed to return any string
        return "Result from Agent ME > AgentReplanner"


def init_agent_me(config: OOConfig, state: State, tracker: Tracker, env: ComputerEnv) -> OOAgentMe:
    logger.debug("Initializing agent-me...")
    return OOAgentMe(config, state, tracker, env)