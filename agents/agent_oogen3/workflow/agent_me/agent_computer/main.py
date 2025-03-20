import logging
from typing import AsyncGenerator, Sequence
from workflow.clients.llm.azure_openai import llm_gpt4o
from workflow.clients.som.omniparser import omniparser
from workflow.tools.keyboard_type import keyboard_type
from workflow.tools.keyboard_hotkeys import keyboard_hotkeys
from workflow.tools.mouse_move import mouse_move
from workflow.tools.mouse_scroll import mouse_scroll
from workflow.tools.mouse_left_click import mouse_left_click
from workflow.tools.mouse_double_click import mouse_double_click
from workflow.tools.find_ui_element import find_ui_element
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import AgentEvent, ChatMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMessageTermination, HandoffTermination, MaxMessageTermination
from autogen_core import CancellationToken
from autogen_agentchat.base import Response
from autogen_core.models import UserMessage
from state import State
from config import OOConfig
from tracker import Tracker

logger = logging.getLogger("agent_me--agent_computer")

SYSTEM_MESSAGE = """
You are `AgentME`, an AI agent responsible for executing **one specific action at a time** within a UI automation workflow. Your role is to follow the provided step, interact with the UI, and return the outcome.

### Agent Capabilities:
- Mouse Move, Click, Double Click, Scroll
- Keyboard Input
- Find UI Element

### Expected Output:
- "Step Completed" if successful.
- "Step Failed: [Reason]" if the action cannot be performed.
"""

USER_MESSAGE = """
For the following plan:
{plan_str}

GOAL: Execute **only** the step: {task}
"""

USER_MESSAGE_WITH_HISTORY = """" 
For the following plan:
{plan_str}

GOAL: Execute **only** the step: {task}

And this is the history of the actions you have already tried:
=========================================
{actions_history}
=========================================
"""


class OOAgentComputer(AssistantAgent):
    def __init__(self, state: State, tracker: Tracker, **kwargs):
        logger.debug("Initializing...")

        name = "agent_me__agent_computer"
        description = "This agent take actions in the computer environment."

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.llm = llm_gpt4o
        self.som = omniparser

        tools = [
            keyboard_type,
            keyboard_hotkeys,
            mouse_move,
            mouse_scroll,
            mouse_left_click,
            mouse_double_click,
            find_ui_element,
        ]

        self.step_counter = 0

        super().__init__(
            name=name, 
            description=description,
            model_client=self.llm, 
            tools=tools, 
            system_message=SYSTEM_MESSAGE,
            **kwargs
        )

    async def on_messages_stream(
        self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken
    ) -> AsyncGenerator[AgentEvent | ChatMessage | Response, None]:
        self.step_counter += 1
        
        # Log the current step
        logger.debug("=================================")
        logger.debug(f"Entity: {self.name} | Local Step: {self.step_counter}")
        logger.debug("=================================")
        logger.info("Predicting ...")
        logger.debug(f"Messages: {messages}")

        # This is the first step in the agent's run
        # step counter is 1
        # and first message with user task is received
        if self.step_counter == 1 and len(messages) > 0:
            logger.debug("First step, messages received.")

            # ---------------------------------------------------------

            # Let's check in the state if there are some previous iterations for this plan step
            past_iterations = self.state.get_current_plan_step_iterations_data()
            
            if len(past_iterations) > 0:
                # We have some past iterations

                actions_history = ""
                for iteration in past_iterations:
                    actions_history += f"Iteration {iteration['iteration_number']}:\n"
                    actions_history += f"Actions: {iteration['iteration_actions']}\n"
                    actions_history += f"Result: {iteration['validation_result']}\n"

                user_message = UserMessage(content=[
                    USER_MESSAGE_WITH_HISTORY.format(
                        plan_str=self.state.current_plan_data["plan_text"],
                        task=messages[0].content,
                        actions_history=actions_history
                    )
                ], source="user")

            else:
                # We don't have any past iterations
                user_message = UserMessage(content=[
                    USER_MESSAGE.format(
                        plan_str=self.state.current_plan_data["plan_text"],
                        task=messages[0].content
                    )
                ], source="user")

            # ---------------------------------------------------------

            # region Log + State + Tracker
            self.tracker.save(f"{self.name}-{self.step_counter}", [
                ("system_message", SYSTEM_MESSAGE),
                ("user_message", user_message),
            ])
            # endregion

            async for response in super().on_messages_stream([user_message], cancellation_token):

                # region Log + State + Tracker
                self.tracker.save(self.name, [
                    ("response", response),
                ])
                # endregion

                yield response

        else:
            # LK TODO: Remove this condition
            if self.step_counter > 1 and len(messages) == 0:
                logger.debug("Another step, no messages received.")
            else: 
                logger.debug("??????? What has happened ???????")
                raise Exception("??????? What has happened ???????")

            # region Log + State + Tracker
            self.tracker.save(f"{self.name}-{self.step_counter}", [
                ("messages", messages),
            ])
            # endregion

            # This is any other step in the agent's run
            async for response in super().on_messages_stream(messages, cancellation_token):

                # region Log + State + Tracker
                self.tracker.save(self.name, [
                    ("response", response),
                ])
                # endregion
                
                yield response


def init_agent_computer(state: State, tracker: Tracker) -> RoundRobinGroupChat:
    logger.debug("Initializing agent_computer team...")

    # Agent
    agent_me = OOAgentComputer(state, tracker)

    config = state.get_config()

    max_messages_termination = MaxMessageTermination(max_messages=config.workflow.params.max_plan_step_actions)
    text_termination = TextMessageTermination(agent_me.name)
    termination = max_messages_termination | text_termination

    # Team 
    team = RoundRobinGroupChat(
            [agent_me],
            termination_condition=termination
        )
    return team