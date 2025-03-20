from typing import Any
from config import OOConfig
from state import State
from workflow.clients.llm import llm_gpt4o, calculate_cost
from autogen_core import Image as AutogenImage
from autogen_core.models import UserMessage, SystemMessage
from tracker import Tracker
from helpers import format_autogen_message

import logging
logger = logging.getLogger("agent_replanner--node_replan")

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
IMPORTANT: Follow strickly the output format to ensure structured execution!!

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

**Last version of the Plan**:
===
{last_plan}
===

**Past Steps**:
===
{past_steps}
===

**Screenshot**:  
[Image Included]

If the objective is fully achieved, reply **"ALL DONE"**. If not, provide an updated plan.
"""

class NodeReplan:
    """
    Responsible for re-planning the execution steps based on past iterations.
    """

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_replanner--node_replan"
        self.description = "Responsible for re-planning the execution steps based on past iterations."

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.llm = llm_gpt4o

    async def execute(self, history: str) -> str:
        logger.debug("Executing...")

        objective = self.config.instruction
        last_plan = self.state.current_plan_data["plan_text"]
        screenshot_t3 = self.state.get_current_plan_image("t3")

        system_message = SystemMessage(content=SYSTEM_MESSAGE)
        user_message = UserMessage(content=[
            USER_MESSAGE.format(
                objective=objective,
                last_plan=last_plan,
                past_steps=history
            ),
            AutogenImage.from_pil(screenshot_t3)
        ], source="user")

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message),
            ("user_message", user_message)
        ])
        # endregion
        
        result = await self.llm.create(
            messages=[
                system_message,
                user_message
            ]
        )

        # ---- COST CALCULATION ----
        model_name, total_cost = calculate_cost(result.usage, self.llm._resolved_model, self.config)
        # ---- END COST CALCULATION ----

        # region Log + State + Tracker
        logger.debug(f"Model: {model_name}, Total cost: {total_cost}$")
        logger.debug(format_autogen_message(result))

        self.tracker.save(self.name, [
            ("llm_response", result),
            ("cost", f"{total_cost}$"),
        ])
        # endregion

        return result.content
        

        