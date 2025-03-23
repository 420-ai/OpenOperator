from clients.llm import llm_gpt4o, llm_llama33, calculate_cost
from clients.computer import ComputerClient
from state import State
from tracker import Tracker
from helpers import encode_image, resize_and_compress_image, fm

import logging
logger = logging.getLogger("agent_planner")

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


class OOPlannerAgent:

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_planner"
        self.description = "Agent responsible for planning"

        self.config = state.get_config()
        self.state = state
        self.tracker = tracker

        # self.llm = llm_gpt4o
        self.llm = llm_llama33

        self.computer = ComputerClient(server_url=f"{self.config.environment.params.server_ip}:{self.config.environment.params.computer_port}")
        

    async def run(self) -> str:
        
        # Log the current step
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

        # Define new messages
        system_message = {"role": "system", "content": SYSTEM_MESSAGE }
        user_message = {
            "role": "user", 
            "content":  [
                {
                    "type": "text",
                    "text":  USER_MESSAGE.format(objective=user_task)
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encode_image(screenshot_t0_resized)}",
                    }
                }
            ]
        }

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message),
            ("user_message", user_message),
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

        # ---- COST CALCULATION ----
        total_cost = calculate_cost(result.usage, self.llm.model, self.config)
        # ---- END COST CALCULATION ----

        # region Log + State + Tracker
        logger.debug(f"Model: {self.llm.model}, Total cost: {total_cost}$")
        logger.debug(fm(result.message))

        self.state.save_plan_text(result.message)

        self.tracker.save(self.name, [
            ("llm_response", result.message),
            ("cost", f"{total_cost}$"),
        ])
        # endregion

def init_agent_planner(state: State, tracker: Tracker) -> OOPlannerAgent:
    logger.debug("Initializing agent-planner...")
    return OOPlannerAgent(state, tracker)