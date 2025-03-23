from core.clients.llm import LLMClient
from core.models import Message, TextContent, ImageContent
from core.state import State
from core.tracker import Tracker
from agent_oo4.helpers import encode_image, fm

import logging
logger = logging.getLogger("agent_me--node_validate_plan_step")

SYSTEM_MESSAGE = """
You are an AI assistant tasked with validating whether a specific objective has been achieved. You will be provided with a detailed plan, a clearly defined objective, and one or more screenshots as evidence. Your role is to analyze the provided information and determine if the objective has been satisfied. 
You don't need to analyze the entire screenshot; focus on the specific elements relevant to the objective. Your response should include a binary conclusion (True or False) and a concise explanation based on the visible evidence in the screenshot(s).

**Guidelines for Validation:**
1. **When a single screenshot is provided:**
   - Focus exclusively on the objective and the visible evidence within the screenshot.
   - Evaluate whether the state or action described in the objective is clearly demonstrated.
   - Example: If the objective is to "click on the message input," confirm that the screenshot shows the input box clicked, selected, or focused.

2. **When two screenshots are provided:**
   - The **first screenshot** represents the state before the action, and the **second screenshot** represents the state after the action.
   - Compare the two images to identify evidence of progression, change, or completion of the described action.
   - Example 1: If the objective is to "select text in an input box," confirm that the second screenshot shows the input box with text selected that was present in the first screenshot.
   - Example 2: If the objective is to "drag and drop an item," verify that the item has moved from its initial position in the first screenshot to its intended target position in the second screenshot.

3. **General and unclear objectives:**
   - Use the plan provided as a contextual guide to interpret the objective and analyze the screenshots effectively.
   - If the screenshots or the objective do not provide sufficient evidence to reach a conclusion, explicitly state this and explain why.

**Response Requirements:**
- Always include a binary conclusion: `True` (objective satisfied) or `False` (objective not satisfied).
- Provide a concise, specific explanation for your conclusion. For example:
  - "True: The text input is selected in the second screenshot, as indicated by the visible underline."
  - "False: The input box is not selected, and no evidence of focus or selection is visible."
- Avoid assumptions not supported by the evidence in the screenshots or the plan.

Consistency, precision, and focus on the objective are essential in your analysis. Use all provided details to make an accurate and justified decision.
"""

USER_MESSAGE = """
Here is the objective:
{objective}

Here is summarization of actions taken:
{actions_history}

Please analyze the provided screenshot(s) and determine if the objective is satisfied based on the following:

1. **For one screenshot:**  
Focus on the visible evidence and its alignment with the objective.  

2. **For two screenshots:**  
The first screenshot represents the state **before** the action, and the second screenshot represents the state **after** the action.  
Compare the images to validate progression, changes, or actions that satisfy the objective. Focus only on the part of the screenshots relevant to the objective. 

Examples:  
- If the objective is "Select text in input box," verify whether the second screenshot shows the input box with the text selected that was present in the first screenshot.  
- If the objective is "Drag and drop item," confirm whether the item has moved from its source position to the target location.

Your response must include:
- A conclusion (`True` or `False`), explicitly stating whether the objective is satisfied.
- A brief explanation detailing the specific evidence from the screenshot(s) that supports your conclusion.

If the objective or evidence is unclear, rely on the plan for additional context and explain why the objective cannot be validated if applicable.
"""

class NodeValidatePlanStep:
    """
    NodeValidatePlanStep is responsible for validating the current plan step.
    """

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_me--node_validate_plan_step"
        self.description = "Validating the current plan step."

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.llm = LLMClient("azure", model="gpt-4o", deployment="gpt-4o-deployment")
        # self.llm = LLMClient("ollama", model="gemma3:27b")

    async def execute(self, actions_history: str) -> bool:
        logger.debug("Executing...")
        
        plan_step = self.state.current_plan_data["plan_step"]["text"]
        screenshot_t1 = self.state.get_current_plan_image("t1_resized")
        screenshot_t2 = self.state.get_current_plan_image("t2_resized")

        # Messages
        system_message = Message(role="system", content=SYSTEM_MESSAGE)
        user_message = Message(
            role="user", 
            content=[
                TextContent(type="text", text=USER_MESSAGE.format(objective=plan_step, actions_history=actions_history)),
                ImageContent(
                    type="image",        
                    data=encode_image(screenshot_t1),
                    media_type="image/png"
                ),
                ImageContent(
                    type="image",        
                    data=encode_image(screenshot_t2),
                    media_type="image/png"
                )
            ]
        )

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message.model_dump()),
            ("user_message", user_message.model_dump()),
            ("screenshot_t1", screenshot_t1),
            ("screenshot_t2", screenshot_t2)
        ])
        # endregion

        result = self.llm.call(
            messages=[
                system_message,
                user_message
            ]
        )

        # region Log + State + Tracker
        cost = f"Provider: {self.llm.provider}, Model: {self.llm.model}, Total cost: {result.usage.cost}$"
        logger.debug(cost)
        logger.debug(fm(result.message.content))

        self.tracker.save(self.name, [
            ("llm_response", result.message.content),
            ("cost", cost),
        ])
        # endregion
        
        return result.message.content