import logging
from typing import Any, AsyncGenerator, List, Sequence
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
import re

logger = logging.getLogger("agent.planner")

SYSTEM_MESSAGE = """You are an AI assistant responsible for breaking down complex tasks into structured, step-by-step plans that an AI agent can execute. Your goal is to ensure that each step is **clear, actionable, and logical**, guiding the agent through a structured problem-solving process.

## **Plan-and-Solve Approach**:
To ensure an optimal solution, follow this structured reasoning process:

### **Step 1: Plan Phase (Decomposing the Task)**
- **Understand the Problem**: Analyze the user’s objective and extract relevant UI elements from the provided screenshot.
- **Devise a Strategy**: Break the objective into **smaller subtasks** before specifying detailed steps.
- **Outline the High-Level Plan**:
  - Determine the key actions required to complete the task.
  - Ensure all necessary steps are included in the plan before execution begins.

### **Step 2: Solve Phase (Executing the Plan)**
- **Execution Plan**: Convert the high-level plan into a strict sequence of **atomic, executable actions** (one per step).
- **Validation & Correction**:
  - Each step must be **precise and self-contained** (no substeps).
  - Align all steps with the agent’s available tools (**Mouse Move, Click, Keyboard Input, etc.**).
  - Ensure that actions are ordered logically to prevent errors or unnecessary repetitions.

### **Step 3: Final Validation**
- **Define Success Criteria**: The last step should verify that the **intended result is achieved**.
- **Adjust if Necessary**: If potential failure points exist, incorporate **self-checks** in the plan to handle failures.

---

## **Output Format**:
**You must strictly follow this format to ensure structured execution.**

```plaintext
### Visual Description:
<Provide a concise description of what is visible in the screenshot.>

### Plan Phase:
<Provide a high-level breakdown of how the task will be solved.>

### Execution Plan:
1. <Step 1: Single, precise action>
2. <Step 2: Next action>
3. <Step 3: Continue execution steps>
...

### Expected Outcome:
- <Describe the final UI state after execution.>
```

---

HINTS:
- if you need to open application, rather search for it, than trying to locate its icon on the desktop.
"""

USER_MESSAGE = """Your objective is: {objective}. Please create a **structured step-by-step plan** that an AI agent can follow using its available tools.

**Screenshot:** [Image Included]
"""


class OOPlannerAgent(BaseChatAgent):

    def __init__(self, config: OOConfig, tracker: Tracker):
        logger.debug("Initializing...")

        name = "agent_planner"
        description = "Agent responsible for planning"

        self.config = config
        self.llm = llm
        self.tracker = tracker

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

        # Get the user task
        user_task = messages[0].content
        
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
            USER_MESSAGE.format(objective=user_task), 
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
    

def init_agent_planner(config: OOConfig, tracker: Tracker) -> OOPlannerAgent:
    logger.debug("Initializing agent-planner...")

    agent = OOPlannerAgent(config, tracker)
    return agent