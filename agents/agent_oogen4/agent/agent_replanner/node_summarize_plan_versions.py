from typing import Any
from config import OOConfig
from state import State
from agent.clients.llm.local_ollama import llm_phi4
from autogen_core import Image as AutogenImage
from autogen_core.models import UserMessage, SystemMessage
import logging
logger = logging.getLogger("agent.replanner-node.summarize_plan_versions")

class NodeSummarizeAllPlanVersions:
   
    def __init__(self, config: OOConfig, state: State):
        logger.debug("Initializing...")

        self.state = state
        self.config = config

    async def execute(self) -> str:
        logger.debug("Executing...")

        result = self.state.get_all_plan_versions_data()

        print("-----")
        print("NodeSummarizeAllPlanVersions")
        print(result)
        print("-----")

        result_str = ""
        for outer_key, inner_dict in result.items():
            result_str += f"=== Version {outer_key} ===\n"
            for inner_key, inner_value in inner_dict.items():
                if inner_key == "plan_step_text":
                    result_str += f"Plan step: {inner_value}\n"
                elif inner_key == "plan_step_result":
                    result_str += f"Result: {inner_value}\n"

        return result_str
    

        
        

        