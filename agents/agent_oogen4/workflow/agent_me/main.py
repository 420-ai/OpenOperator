import sys
import json
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
from workflow.agent_me.agent_take_actions.main import AgentTakeActions
# from workflow.agent_me.node_create_actions.main_without_tools import NodeCreateActions
# from workflow.agent_me.node_create_actions.main_with_tools import NodeCreateActions
from workflow.agent_me.node_create_actions.custom_main_with_tools import NodeCreateActions
from clients.computer import computer
from environment.computer.env import ComputerEnv
import numpy as np
from autogen_core.models import FunctionExecutionResult
from pprint import pprint

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
        self.nodeCreateActions = NodeCreateActions(config, state, tracker)
        self.agentTakeActions = AgentTakeActions(config, state, tracker, self.computerEnv)
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
        # isDone = await self.nodeIsStepDone.execute()
        # if isDone == True:
        #     return "AgenMe is done with the step, because it is already done"

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

            # ----------------------
            # Capture state before action
            # ----------------------
            screenshot_t1 = self.computer.get_screenshot()
            self.state.save_plan_image(screenshot_t1, "t1.png")

            screenshot_t1_resized = resize_and_compress_image(screenshot_t1)
            self.state.save_plan_image(screenshot_t1_resized, "t1_resized.png")

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


            all_messages = await self.agentTakeActions.run()

            


            # # ----------------------
            # # ----------------------
            # # PLAN STEP - ACTIONS LOOP
            # # ----------------------
            # # ----------------------
            # plan_step_actions_cycles = 0
            # plan_step_actions_messages = []
            # while plan_step_actions_cycles < self.config.workflow.params.max_plan_step_actions:
            #     plan_step_actions_cycles += 1

            #     logger.debug("--------------------------")
            #     logger.debug(f"Plan step - Actions iteration: {plan_step_actions_cycles}")
            #     logger.debug("--------------------------")
            #     print("messages")
            #     print(plan_step_actions_messages)


            #     response, actions_json = await self.nodeCreateActions.execute(plan_step_actions_messages)

            #     # Custom implementation of TextMessageTermination
            #     if response.choices[0].finish_reason != "tool_calls":
            #         logger.debug("TextMessageTermination, end the loop")
            #         break

            #     logger.debug(f"Actions: {actions_json}")

            #     print("Aaaaaaaaaaaa")
            #     print(response.choices[0].message)
            #     message_json = response.choices[0].message.model_dump_json()
            #     print(message_json)


            #     # Add message to the list of messages
            #     plan_step_actions_messages.append(message_json)

            #     # ----------------------
            #     # Take actions in the environment
            #     # ----------------------
            #     # Loop through messages and actions
            #     for action in actions_json:
            #         # Take action in the environment
            #         action_type = str(action["action"])
            #         params = json.dumps(action["parameters"])

            #         data = (action_type, params)
            #         obs, reward, terminated, truncated, info = self.computerEnv.step(data)

            #         # Add the tool result to the list of messages
            #         msg = {
            #             "role": "tool",
            #             "tool_call_id": action["id"],  
            #             "name": action["action"],
            #             "content": json.dumps(action["parameters"]),
            #         }
            #         plan_step_actions_messages.append(msg)










            #     # messages, actions_json = await self.nodeCreateActions.execute(plan_step_actions_messages)


            #     # # Custom implementation of TextMessageTermination
            #     # if type(messages) == str:
            #     #     logger.debug("TextMessageTermination, end the loop")
            #     #     break
            #     # else:
            #     #     # Add messages to the list of messages
            #     #     plan_step_actions_messages.extend(messages)

            #     # print("messages 2")
            #     # print(plan_step_actions_messages)

            #     # # region Log + State + Tracker
            #     # logger.debug(f"Actions: {actions_json}")
            #     # # endregion

            #     # # ----------------------
            #     # # Take actions in the environment
            #     # # ----------------------
            #     # # Loop through messages and actions
            #     # for index in range(len(actions_json)):
            #     #     message = messages[index]
            #     #     action = actions_json[index]

            #     #     # Add message to the list of messages
            #     #     plan_step_actions_messages.append(message)

            #     #     # Take action in the environment
            #     #     action_type = str(action["action"])
            #     #     params = json.dumps(action["parameters"])

            #     #     data = (action_type, params)
            #     #     obs, reward, terminated, truncated, info = self.computerEnv.step(data)

            #     #     # Add the tool result to the list of messages
            #     #     plan_step_actions_messages.append(info["tool_result"])


            #     print(f"Plan step actions loop '{plan_step_actions_cycles}' finished.")

            # print("-------------------------")
            # print("-------------------------")
            # print("-------------------------")
            # print("-------------------------")
            # print("-------------------------")
            # print("-------------------------")
            # print("-------------------------")
            # print("-------------------------")
            # print("We break out of the plan step actions loop")

            # print("ALL MESSAGES")
            # pprint(plan_step_actions_messages)

            
            # ----------------------
            # Capture state after action
            # ----------------------
            screenshot_t2 = self.computer.get_screenshot()
            screenshot_t2_resized = resize_and_compress_image(screenshot_t2)

            # ----------------------
            # Summarize the actions taken
            # ----------------------
            actions_summarization = await self.nodeSummarizeActions.execute(all_messages)

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

            planStepValidation = isStepDone

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