from config import OOConfig
from state import State
from agent.clients.llm.azure_openai import llm_gpt4o
from autogen_core import Image as AutogenImage
from autogen_core.models import UserMessage, SystemMessage
from PIL import Image
from agent.agent_me.agent_take_actions import init_agent_take_action

class NodeTakeActions:
    """
    Take actions and control computer.
    """

    def __init__(self, config: OOConfig, state: State):
        self.state = state
        self.config = config

        self.llm = llm_gpt4o



    async def execute(self, screenshot_t1: Image.Image) -> bool:

        plan_step = self.state.current_plan_data["plan_step"]["text"]

        ## Get the history of the plan step iterations
        ## TBD

        agent = init_agent_take_action(self.config, self.state)

        
        
        
        return first_step.content