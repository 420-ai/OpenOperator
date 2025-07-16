from typing import Any
from state import State
from tracker import Tracker
from clients.llm import llm_mistral, calculate_cost
from helpers import fm
from workflow.agent_me.helpers import trim_user_message

import logging
logger = logging.getLogger("agent_me--node_summarize_actions")

SYSTEM_MESSAGE = """
You are an AI assistant that summarizes a sequence of actions into a short, concise summary.

Instructions:
- Only output the summarization itself.
- Do not include any introductory or explanatory text.
- Do not repeat or restate the input.
- Do not speculate or add context.
- Your output must be factual, minimal, and strictly based on the provided actions.

Output format:
<single concise summary, no headings, no lists, no extra commentary>
"""

USER_MESSAGE = """
Goal of the actions:
===========================
{plan_step}
===========================

Actions that occurred:
===========================
{messages}
===========================
"""

class NodeSummarizeActions:
    """
    Summarize actions
    """

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_me--node_summarize_actions"
        self.description = "Summarize actions."

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.llm = llm_mistral

    async def execute(self, messages: Any) -> bool:
        logger.debug("Executing...")

        print(type(messages))
        print(messages)

        print(type(messages[0]))
        print(messages[0])

        filtered_messages = []
        for message in messages:
            print(type(message))

            if message["role"] == "system":
                continue
            if message["role"] == "user":
                shortened_text = trim_user_message(message)
                filtered_messages.append(shortened_text)
            else:
                filtered_messages.append(message)


        print("Filtered messages:")
        print(filtered_messages)


        plan_step = self.state.current_plan_data["plan_step"]["text"]
        
        system_message = {"role": "system", "content": SYSTEM_MESSAGE }
        user_message = {
            "role": "user", 
            "content": USER_MESSAGE.format(plan_step=plan_step, messages=filtered_messages)
        }

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message),
            ("user_message", user_message)
        ])
        # endregion

        result = self.llm.call(
            messages=[
                system_message,
                user_message
            ]
        )

        # ---- COST CALCULATION ----
        total_cost = calculate_cost(result.usage, self.llm.model, self.config)
        # ---- END COST CALCULATION ----

        # region Log + State + Tracker
        logger.debug(f"Model: {self.llm.model}, Total cost: {total_cost}$")
        logger.debug(fm(result.message))

        self.tracker.save(self.name, [
            ("llm_response", result.message),
            ("cost", f"{total_cost}$"),
        ])
        # endregion
        
        return result.message