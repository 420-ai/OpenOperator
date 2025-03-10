import logging
from typing import Any, AsyncGenerator, Sequence
from agent.clients.llm.azure_openai import llm
from agent.clients.computer.server_client import get_screenshot
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.messages import AgentEvent, ChatMessage, TextMessage, MultiModalMessage
from autogen_core import CancellationToken
from autogen_agentchat.base import Response
from autogen_core.models import UserMessage, SystemMessage
from autogen_core import Image
from agent.helpers import encode_image, resize_and_compress_image
from autogen_agentchat.utils import content_to_str
from tracker import Tracker
from config import OOConfig

logger = logging.getLogger("agent.replanner")

SYSTEM_MESSAGE = """You are the `Replanner`, responsible for analyzing and updating the execution plan based on past results. Your goal is to ensure that the user’s objective is fully achieved by evaluating execution progress and refining the plan if needed.

## **Plan-and-Solve Approach**:
To ensure optimal completion of the task, follow this structured reasoning process:

### **Step 1: Analyze Execution Progress**
- **Review Completed Steps**: Check the past execution steps and verify their correctness.
- **Identify Issues**: Determine if a step failed, was incomplete, or needs adjustment.
- **Decide Next Action**:
  - If **the objective is fully achieved**, return `"ALL DONE"`.
  - If **modifications are required**, generate a revised plan with clear execution steps.

### **Step 2: Refine the Plan**
- **Update the Execution Plan**: Modify or append necessary steps while ensuring clarity and correctness.
- **Follow Strict Formatting**:
  - The first line must be `### Execution Plan:`
  - Steps must be formatted as `1.`, `2.`, `3.`, etc.
  - No substeps or section headers within the execution steps.
- **Ensure Atomic Steps**: Each step must be a single, executable action.
- **Align with Available Tools**: Keep the steps actionable using **Mouse Move, Click, Keyboard Input, etc.**.

### **Step 3: Validation & Expected Outcome**
- **Define Success Criteria**: The final step should verify that the **intended result is achieved**.
- **Remove Redundant Steps**: Optimize the plan to prevent unnecessary actions.

---

## **Output Format**:

**If the task is complete, return:**
```plaintext
ALL DONE
```

**If modifications are required, return:**
```plaintext
### Execution Plan:
1. <Step 1: Single, precise action>
2. <Step 2: Next action>
3. <Step 3: Continue execution steps>
...

### Expected Outcome:
- <Describe the final UI state after execution.>
```
"""

USER_MESSAGE = """
Please evaluate the execution results and determine if the task is complete or requires further action.

**Objective**:
===
{objective}
===

**Original Plan**:
===
{plan}
===

**Past Steps**:
===
{past_steps}
===

**Screenshot**:  
[Image Included]

If the objective is fully achieved, reply **"ALL DONE"**. If not, provide an updated plan.
"""

class OOReplannerAgent(BaseChatAgent):

    def __init__(self, config: OOConfig, tracker: Tracker, objective: str, plan: str, past_steps: str):
        logger.debug("Initializing...")

        name = "agent_replanner"
        description = "Agent responsible for replanning"

        self.config = config
        self.llm = llm
        self.tracker = tracker

        self.objective = objective
        self.plan = plan
        self.past_steps = past_steps

        super().__init__(
            name, 
            description,
        )
        

    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        return (TextMessage,)

    async def _inner_on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Any:
        self.tracker.set_entity_step(self.name)
        
        # Log the current step
        logger.debug("=================================")
        logger.debug(f"Entity: {self.name} - Global Step: {self.tracker.step_counter}")
        logger.debug("=================================")

        logger.info("Predicting ...")

        # Take a screenshot
        screenshot = get_screenshot()
        self.tracker.save_origin_screenshot(screenshot)

        # Resize and compress the screenshot
        screenshot_resized = resize_and_compress_image(screenshot)
        self.tracker.save_resized_screenshot(screenshot_resized)

        # Define new messages
        system_message = SystemMessage(content=SYSTEM_MESSAGE)
        self.tracker.save_system_message(system_message)

        user_message = UserMessage(content=[
            USER_MESSAGE.format(
                objective=self.objective,
                plan=self.plan,
                past_steps=self.past_steps
            ), 
            Image.from_pil(screenshot_resized)
        ], source="user")
        self.tracker.save_user_message(user_message)
        
        # Call LLM
        result = await self.llm.create(messages=[
            system_message,
            user_message,
        ])

        # Construct response message
        response_message = TextMessage(content=result.content, source=self.name)
        self.tracker.save_response(response_message)

        return response_message

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        result = await self._inner_on_messages(messages, cancellation_token)
        return Response(chat_message=result)
    
    async def on_messages_stream(
        self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken
    ) -> AsyncGenerator[AgentEvent | ChatMessage | Response, None]:
        result = await self._inner_on_messages(messages, cancellation_token)
        yield Response(
            chat_message=result,
            inner_messages=[],
        )

    async def on_reset(self, cancellation_token):
        return await super().on_reset(cancellation_token)
    

def init_agent_replanner(config: OOConfig, tracker: Tracker, objective: str, plan: str, past_steps: str) -> OOReplannerAgent:
    logger.debug("Initializing agent-replanner...")

    agent = OOReplannerAgent(config, tracker, objective, plan, past_steps)
    return agent