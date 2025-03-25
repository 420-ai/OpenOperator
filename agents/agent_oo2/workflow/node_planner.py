from core.clients.llm import LLMClient
from core.models import Message, TextContent, ImageContent
from core.clients.computer import ComputerClient
from core.state import State
from core.tracker import Tracker
from agent_oo2.helpers import encode_image, resize_and_compress_image, fm

import logging
logger = logging.getLogger("node_planner")

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


class OOPlannerNode:

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "node_planner"
        self.description = "Node responsible for planning"

        self.config = state.get_config()
        self.state = state
        self.tracker = tracker

        self.llm = LLMClient("azure", model="gpt-4o", deployment="gpt-4o-deployment")
        # self.llm = LLMClient("openai", model="gpt-4o")
        # self.llm = LLMClient("ollama", model="llama3.2-vision:latest")
        # self.llm = LLMClient("anthropic", model="claude-3-7-sonnet-20250219")

        self.computer = ComputerClient()
        

    async def execute(self) -> str:
        logger.debug("=================================")
        logger.debug(f"Entity: {self.name}")
        logger.debug("=================================")
        logger.info("Predicting ...")
        self.state.create_new_plan_version()

        # Get the user task
        user_task = self.config.instruction
        
        # Take a screenshot
        screenshot_t0 = self.computer.get_screenshot()

        # Resize and compress the screenshot
        screenshot_t0_resized = resize_and_compress_image(screenshot_t0)
        self.state.save_plan_image(screenshot_t0_resized, "t0.png")

        # Messages
        system_message = Message(role="system", content=SYSTEM_MESSAGE)
        user_message = Message(
            role="user", 
            content=[
                TextContent(type="text", text=USER_MESSAGE.format(objective=user_task)),
                ImageContent(
                    type="image",        
                    data=encode_image(screenshot_t0_resized),
                    media_type="image/png"
                )
            ]
        )

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message.model_dump()),
            ("user_message", user_message.model_dump()),
            ("screenshot_t0_resized", screenshot_t0_resized)
        ])
        # endregion
        
        # Call LLM
        result = self.llm.call(
            messages=[
                system_message,
                user_message,
            ]
        )

        # region Log + State + Tracker
        cost = f"Provider: {self.llm.provider}, Model: {self.llm.model}, Total cost: {result.usage.cost}$"
        logger.debug(cost)
        logger.debug(fm(result.message.content))

        self.state.save_plan_text(result.message.content)

        self.tracker.save(self.name, [
            ("llm_response", result.message.content),
            ("cost", cost),
        ])
        # endregion
