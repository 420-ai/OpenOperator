from config import OOConfig
from state import State
from tracker import Tracker
from clients.llm import llm_gpt4o, calculate_cost
from clients.som import omniparser
from autogen_core import Image as AutogenImage
from autogen_core.models import UserMessage, SystemMessage
from helpers import format_autogen_message
import json

import logging
logger = logging.getLogger("agent_me--node_create_actions")

SYSTEM_MESSAGE = """
You are an AI assistant responsible for generating a set of automated actions based on a given textual description and an accompanying screenshot. Your goal is to interpret the provided inputs and generate a structured list of actions in the expected JSON format.

### **Guidelines for Generating Actions:**
1. **Understand the Context**  
   - Carefully analyze the given textual description to identify the intended goal.  
   - If a screenshot is provided, interpret the visual elements to support the description.

2. **Break Down the Required Actions**  
   - Identify the sequence of actions needed to achieve the goal.  
   - Actions may involve moving the mouse, clicking, typing text, pressing hotkeys, or scrolling.  
   - Ensure the actions are logically ordered.

3. **Use the Correct Action Format**  
   - Each action must follow this JSON structure:
     ```json
     {
         "action": "<action_name>",
         "parameters": { <parameters_object> }
     }
     ```
   - Available actions:
     - **`keyboard_hotkeys`**: Press a combination of hotkeys.
       ```json
       { "action": "keyboard_hotkeys", "parameters": { "hotkeys": ["ctrl", "c"] } }
       ```
     - **`keyboard_type`**: Type a given text.
       ```json
       { "action": "keyboard_type", "parameters": { "text": "Hello, world!" } }
       ```
     - **`mouse_double_click`**: Perform a double-click.
       ```json
       { "action": "mouse_double_click", "parameters": {} }
       ```
     - **`mouse_left_click`**: Perform a single left-click.
       ```json
       { "action": "mouse_left_click", "parameters": {} }
       ```
     - **`mouse_move`**: Move the mouse cursor to a specific (x, y) coordinate.
       ```json
       { "action": "mouse_move", "parameters": { "x": 500, "y": 300 } }
       ```
     - **`mouse_scroll`**: Scroll up, down, left, or right.
       ```json
       {
         "action": "mouse_scroll",
         "parameters": { "direction": "down", "amount": 3, "delay": 0.1, "steps": 2 }
       }
       ```
   
4. **Ensure Accuracy and Efficiency**  
   - Avoid redundant actions.  
   - Use minimal necessary steps to accomplish the task.  
   - Actions should be as precise as possible, e.g., moving the cursor to a relevant UI element before clicking.

5. **Output Example**  
   If the description states:  
   _"Copy the selected text from the document and paste it into the search bar."_  
   
   The expected output should be:
   ```json
   [
       { "action": "keyboard_hotkeys", "parameters": { "hotkeys": ["ctrl", "c"] } },
       { "action": "mouse_move", "parameters": { "x": 400, "y": 150 } },
       { "action": "mouse_left_click", "parameters": {} },
       { "action": "keyboard_hotkeys", "parameters": { "hotkeys": ["ctrl", "v"] } }
   ]
   ```

6. **Handling Screenshots**  
   - If a screenshot is provided, use it to infer the required UI elements.  
   - Example: If the text description says, _"Click the submit button,"_ and the screenshot shows the button at coordinates `(620, 350)`, the system should generate:
     ```json
     [
         { "action": "mouse_move", "parameters": { "x": 620, "y": 350 } },
         { "action": "mouse_left_click", "parameters": {} }
     ]
     ```

### **Final Instructions**
- Ensure that all generated actions follow the required JSON format.  
- Prioritize efficiency while maintaining correctness.  
- If any required details are missing (e.g., exact coordinates), make reasonable assumptions based on common UI patterns.
- DO NOT FORMAT THE OUTPUT AS A MARKDOWN CODE BLOCK. RETURN THE JSON DIRECTLY.
"""

USER_MESSAGE = """
Here is the textual description, please generate a list of actions.
=========================
{plan_step}
=========================

Attached is current screenshot including ID of UI elements. Each UI element has a unique ID and you can see their coordinates below.
=========================
{ui_elements}
=========================
"""

class NodeCreateActions:
    """
    Check if the step is done.
    """

    def __init__(self, config: OOConfig, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_me--node_create_actions"
        self.description = "This node's responsibility is to generate actions (for environment) based on the plan step."

        self.state = state
        self.config = config
        self.tracker = tracker

        self.llm = llm_gpt4o
        self.som = omniparser

    async def execute(self) -> bool:
        logger.debug("Executing...")
        
        # Get the plan step from state
        plan_step = self.state.current_plan_data["plan_step"]["text"]
        # Get the screenshot from state
        screenshot_t1 = self.state.get_current_plan_image("t1")
        
        # Analyze the screenshot and get the UI elements
        parsed = self.som.analyze_image(screenshot_t1)

        system_message = SystemMessage(content=SYSTEM_MESSAGE)
        user_message = UserMessage(content=[
            USER_MESSAGE.format(
                plan_step=plan_step,
                ui_elements=parsed["parsed_content_list"]
            ),
            AutogenImage.from_pil(parsed["parsed_image"]) 
        ], source="user")

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message),
            ("user_message", user_message),
            ("parsed_screenshot", parsed["parsed_image"])
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

        try:
            result_json = json.loads(result.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {e}")
            raise ValueError("Invalid JSON format in the response.")

        print(type(result_json))
        print(type(result_json[0]))
        print(result_json)

        return result_json
    
