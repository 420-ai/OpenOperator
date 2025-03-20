import logging
from clients.llm import my_llm_gpt4o, my_calculate_cost
from state import State
from tracker import Tracker

logger = logging.getLogger("node_summarize")

SYSTEM_MESSAGE = """You are a summarizer agent. Your task is to create a concise and clear summary of the actions taken.
"""

USER_MESSAGE = """Here are the actions taken by the agent:
{history}
"""


class OONodeSummarize:

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "node_summarize"
        self.description = "Node responsible for summarizing the actions taken by the agent."

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.llm = my_llm_gpt4o

    async def execute(self) -> str:
        
        # Log the current step
        logger.debug("=================================")
        logger.debug(f"Entity: {self.name}")
        logger.debug("=================================")
        logger.debug("Executing...")

        # ----------------------
        # Format all steps taken in the plan
        # ----------------------
        result = self.state.get_all_plan_versions_data()

        history = ""
        for outer_key, inner_dict in result.items():
            history += f"=== Version {outer_key} ===\n"
            for inner_key, inner_value in inner_dict.items():
                if inner_key == "plan_step_text":
                    history += f"Plan step: {inner_value}\n"
                elif inner_key == "plan_step_result":
                    history += f"Result: {inner_value}\n"

        # ----------------------
        # Summarize
        # ----------------------
        system_message = {"role": "system", "content": SYSTEM_MESSAGE}
        user_message = {
            "role": "user", 
            "content":  USER_MESSAGE.format(history=history)
        }

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message),
            ("user_message", user_message)
        ])
        # endregion
        
        # Call LLM
        result = await self.llm.call(messages=[
            system_message,
            user_message,
        ])

        # ---- COST CALCULATION ----
        model_name, total_cost = my_calculate_cost(result.usage.prompt_tokens, result.usage.completion_tokens, self.llm.model, self.config)
        # ---- END COST CALCULATION ----

        # region Log + State + Tracker
        logger.debug(f"Model: {model_name}, Total cost: {total_cost}$")
        logger.debug(result.to_json())

        self.tracker.save(self.name, [
            ("llm_response", result.to_json()),
            ("cost", f"{total_cost}$"),
        ])
        # endregion

        # ?????
        if len(result.choices) > 1:
            print(result.choices)
            raise ValueError("Multiple choices returned, expected only one. -------> INVESTIGATE")

        return result.choices[0].message.content
