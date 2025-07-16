import logging
import re
from typing import Dict, List
from io import BytesIO
from PIL import Image

from my_utils import save_to_json, save_base64_to_png, save_image
from agent.llm_clients.azure_openai import AzureOpenAIClient
from agent.llm_clients.messages import planning_system_message_shortened_previmg, build_user_msg_visual
from agent.helpers import remove_min_leading_spaces, prev_actions_to_string, resize_image_openai
from agent.som_clients.omniparser import OmniparserClient
from agent.som_clients.obs import parser_to_prompt

logger = logging.getLogger("agent.main")

class OOAgent:
    def __init__(
            self,
            model: str = "gpt-4o", # openai or "phi3-v"
            temperature: float = 0.5,
            # ???
            use_last_screen = True,
            obs_view = "screen", # "screen" or "window"
    ):
        logger.debug("Initializing...")

        self.model = model
        self.som_client = OmniparserClient()
        self.llm_client = AzureOpenAIClient(deployment_name=self.model, temperature=temperature)
        

        # ???
        self.action_space = "code_block"
        self.obs_view = obs_view
        self.last_image = None
        
        self.use_last_screen = use_last_screen
        if use_last_screen:
            self.llm_client.system_prompt = planning_system_message_shortened_previmg

        self.parser_to_prompt = parser_to_prompt

        self.memory_block_text_empty = """
```memory
# empty memory block
```
"""
        self.memory_block_text = self.memory_block_text_empty

        self._prev_actions = []
        self._clipboard_content = None
        self._n_prev = 15
        self._step_counter = 0
      

    def predict(self, instruction: str, obs: Dict) -> List:
        """
        Predict the next action(s) based on the current observation.
        """
        logger.info("Predicting...")
        self._step_counter += 1
        logs={}

        if self.obs_view == "screen":
            view_image = obs['screenshot']
            view_rect = [0, 0, view_image.width, view_image.height]
        else:
            view_image = obs['window_image']
            view_rect = obs['window_rect']

        save_image(view_image, "view_image.png")

        # --------------------------------
        # SoM - Omniparser = extract regions
        # --------------------------------
        logger.info("Analysing screenshot with Omni ...")
        result = self.som_client.propose_ents(view_image, with_captions=True)
        regions = result["parsed_content_list"]
        parsed_image = result["parsed_image"]
        save_to_json(regions, "parsed_image_regions.json")
        save_image(parsed_image, "parsed_image.png")
        logger.info("Screenshot analysed with omni")

        # All rectangles on the image
        rects = [[int(ent["shape"]["x"]), int(ent["shape"]["y"]), int((ent["shape"]["x"]+ent["shape"]["width"])), int((ent["shape"]["y"]+ent["shape"]["height"]))] for ent in regions]

        # full set-of-marks drawing w/ visibility filtering, overlap detection, and colors
        color_mapping_debug = {"image": "red", "text": "blue", "icon": "green"}
        color_mapping_prompt = {"image": "red", "icon": "green"}
        image_debug, image_prompt, list_of_text = self.parser_to_prompt(view_image, regions, color_mapping_debug, color_mapping_prompt) 
        
        save_image(image_debug, "image_debug.png")
        save_image(image_prompt, "image_prompt.png")

        # Logs for debugging
        logs['parsed_image'] = parsed_image
        logs['foreground_window'] = view_image
        logs['foreground_window_regions'] = image_debug
        logs['foreground_window_prompt'] = image_prompt
        logs['window_title'] = obs['window_title']
        logs['window_names_str'] = obs['window_names_str']
        logs['computer_clipboard'] = obs['computer_clipboard']
        logs['image_width'] = view_image.width
        logs['image_height'] = view_image.height
        logs['regions'] = regions
        # --------------------------------
        # --------------------------------

        # Previous actions
        prev_actions_str = prev_actions_to_string(
            self._prev_actions, 
            self._n_prev
        )

        # User prompt ---------
        user_prompt = build_user_msg_visual(
            instruction, 
            obs['window_title'], 
            obs['window_names_str'], 
            obs['computer_clipboard'], 
            "N/A", 
            list_of_text, 
            prev_actions_str, 
            self.memory_block_text
        )
        logs['user_prompt'] = user_prompt
        
         # Image prompt --------
        image_resized, w_resized, h_resized, factor = resize_image_openai(view_image)
        image_prompt_resized, w_resized, h_resized, factor = resize_image_openai(image_prompt)
        
        save_image(image_resized, "image_resized.png")
        save_image(image_prompt_resized, "image_prompt_resized.png")

        image_prompts = [image_resized, image_prompt_resized]
        if self.use_last_screen:
            last_image = self.last_image if self.last_image is not None else image_resized
            self.last_image = image_resized
            logs['last_image'] = last_image

            save_image(last_image, "last_image.png")
            save_image(self.last_image, "self_last_image.png")
            
            #image_prompts = [last_image] + image_prompts
            image_prompts = [last_image, image_prompt_resized]

            logger.debug("Image prompts = [last_image, image_prompt_resized]")
        else:
            logger.debug("Image prompts = [image_resized, image_prompt_resized]")


        # ??? Is this correct ??
        scale = (
            obs['screenshot'].width/view_image.width, 
            obs['screenshot'].height/view_image.height
        )

        computer_update_args = {
            'rects': rects,
            'window_rect': view_rect,
            'screenshot': obs['screenshot'],
            'scale': scale,
            'clipboard_content': obs['computer_clipboard'],
            'swap_ctrl_alt': False
        }


        # --------------------------------
        # LLM call
        # --------------------------------
        logger.info("Calling LLM...")
        plan_request, plan_result = self.llm_client.plan(image_prompts, user_prompt)
        logger.info("LLM responded")

        logs['plan_request'] = plan_request
        logs['plan_result'] = plan_result

        # --------------------------------
        # Process the LLM response
        # --------------------------------

        # extract the textual memory block
        memory_block = re.search(r'```memory\n(.*?)```', plan_result, re.DOTALL)
        if memory_block:
            self.memory_block_text = '```memory\n' + memory_block.group(1) + '```'

        logger.debug("Memory block:\n %s", self.memory_block_text)

        # extract the plan which is in a ```python ...``` code block
        code_block = re.search(r'```python\n(.*?)```', plan_result, re.DOTALL)
        if code_block:
            code_block_text = code_block.group(1)
            code_block_text = remove_min_leading_spaces(code_block_text)
            actions = [code_block_text]
        else:
            logger.error("Plan not found")
            code_block_text = "# plan not found"
            actions = ["# plan not found"]

        logger.debug("Code block:\n %s", code_block_text)

        # ??? For what ???
        self._prev_actions.append(code_block_text)

        # extract the high-level decision block
        decision_block = re.search(r'```decision\n(.*?)```', plan_result, re.DOTALL)
        if decision_block:
            decision_block_text = decision_block.group(1)
            if "DONE" in decision_block_text:
                actions = ["DONE"]
            elif "FAIL" in decision_block_text:
                actions = ["FAIL"]
            elif "WAIT" in decision_block_text:
                actions = ["WAIT"]

            logger.debug("Decision block:\n %s", decision_block_text)

        return actions, logs, computer_update_args


    def reset(self):
        logger.info("reset()")
        self.memory_block_text = self.memory_block_text_empty
        self._prev_actions = []
        self._clipboard_content = None
        self._step_counter = 0
        self.last_image = None