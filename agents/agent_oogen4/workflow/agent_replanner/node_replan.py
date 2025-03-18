from typing import Any
from config import OOConfig
from state import State
from clients.llm import llm_gpt4o
from autogen_core import Image as AutogenImage
from autogen_core.models import UserMessage, SystemMessage
import logging

logger = logging.getLogger("agent.replanner-node.replan")

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

    def __init__(self, config: OOConfig, state: State):
        logger.debug("Initializing...")

        self.state = state
        self.config = config

        self.llm = llm_gpt4o

    async def execute(self, history: str) -> str:
        logger.debug("Executing...")

        objective = self.config.instruction
        last_plan = self.state.current_plan_data["plan_text"]
        screenshot_t3 = self.state.get_current_plan_image("t3")
        
        replan_result = await self.llm.create(
            messages=[
                SystemMessage(content=SYSTEM_MESSAGE),
                UserMessage(content=[
                    USER_MESSAGE.format(
                        objective=objective,
                        last_plan=last_plan,
                        past_steps=history
                    ),
                    AutogenImage.from_pil(screenshot_t3)
                ], source="user")
            ]
        )

        return replan_result.content
        

        