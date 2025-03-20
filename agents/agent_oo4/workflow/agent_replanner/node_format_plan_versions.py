from state import State
from tracker import Tracker

import logging
logger = logging.getLogger("agent_replanner--node_format_plan_versions")

class NodeFormatAllPlanVersions:
   
    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_replanner--node_format_plan_versions"
        self.description = "Format all plan versions."

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

    async def execute(self) -> str:
        logger.debug("Executing...")

        result = self.state.get_all_plan_versions_data()

        result_str = ""
        for outer_key, inner_dict in result.items():
            result_str += f"=== Version {outer_key} ===\n"
            for inner_key, inner_value in inner_dict.items():
                if inner_key == "plan_step_text":
                    result_str += f"Plan step: {inner_value}\n"
                elif inner_key == "plan_step_result":
                    result_str += f"Result: {inner_value}\n"

        # region Log + State + Tracker
        logger.debug(result_str)

        self.tracker.save(self.name, [
            ("plan_versions_formatted", result_str),
        ])
        # endregion

        return result_str
    

        
        

        