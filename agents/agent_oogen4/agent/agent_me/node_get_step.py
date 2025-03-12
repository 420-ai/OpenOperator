from config import OOConfig
from state import State
from agent.clients.llm.local_ollama import llm_phi4
from autogen_core.models import UserMessage, SystemMessage

SYSTEM_MESSAGE = """
You are a helpful assistant that helps the user to get the first step of the plan.
"""

USER_MESSAGE = """
Here is the plan, return the first step of the plan:
{plan}
"""

class NodeGetStep:
    """
    Get the first step from the plan.
    """

    def __init__(self, config: OOConfig, state: State):
        self.state = state
        self.config = config

        self.llm = llm_phi4

    async def execute(self) -> None:

        # Get the plan from state
        plan = self.state.current_plan_data["plan_text"]
        print(plan)

        # LLM call
        first_step = await self.llm.create(
            messages=[
                SystemMessage(content=SYSTEM_MESSAGE),
                UserMessage(content=[
                    USER_MESSAGE.format(plan=plan), 
                ], source="user")
            ]
        )
        print(first_step)

        # Save the first step in the state
        self.state.save_plan_step_text(first_step.content)
        