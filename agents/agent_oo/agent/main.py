import logging
import re
from typing import Dict, List
from io import BytesIO
from PIL import Image

from my_utils import save_to_json, save_base64_to_png
from agent.llm_clients.azure_openai import AzureOpenAIClient
from agent.llm_clients.messages import planning_system_message_shortened_previmg, build_user_msg_visual
from agent.helpers import remove_min_leading_spaces, prev_actions_to_string, resize_image_openai
from agent.som_clients.omniparser import OmniparserClient
from agent.som_clients.obs import parser_to_prompt

logger = logging.getLogger("agent_oo.main")

class OOAgent:
    def __init__(
            self,
            model: str = "gpt-4o", # openai or "phi3-v"
            temperature: float = 0.5,
            use_last_screen = True,
    ):
        self.action_space = "code_block"
        self.model = model
        self.use_last_screen = use_last_screen
        self.last_image = None

        self.som_client = OmniparserClient()
        self.llm_client = AzureOpenAIClient(deployment_name=self.model, temperature=temperature)
        if use_last_screen:
            self.llm_client.system_prompt = planning_system_message_shortened_previmg


        
        
        self.parser_to_prompt = parser_to_prompt

        self.memory_block_text_empty = """
```memory
# empty memory block
```
"""
        self.memory_block_text = self.memory_block_text_empty

        self.prev_actions = []
        self.clipboard_content = None
        self.n_prev = 15
        self.step_counter = 0
      

    def predict(self, instruction: str, obs: Dict) -> List:
        """
        Predict the next action(s) based on the current observation.
        """
        print("Agent predict()")
        logs={}
        
        image_file = BytesIO(obs['screenshot'])
        view_image = Image.open(image_file)
        view_rect = [0, 0, view_image.width, view_image.height]
        
        window_title, window_names_str, window_rect, computer_clipboard = obs['window_title'], obs['window_names_str'], obs['window_rect'], obs['computer_clipboard']
        original_h, original_w = view_image.height, view_image.width
        
        override_plan = False
           
        if not override_plan:
            logger.info("Processing screenshot...")
            
            image  = view_image
            w,h = original_w, original_h
            logs['foreground_window'] = image
            
            # --------------------------------
            # extract regions - OMNI
            # --------------------------------
            print("Analysing screenshot with omni")

            # omni extractor
            rendering = "N/A"
            regions = self.som_client.propose_ents(image, with_captions=True)

            save_to_json(regions, "regions_new.json")

            print("Screenshot analysed with omni")


            rects = [[int(ent["shape"]["x"]), int(ent["shape"]["y"]), int((ent["shape"]["x"]+ent["shape"]["width"])), int((ent["shape"]["y"]+ent["shape"]["height"]))] for ent in regions]
            color_mapping_debug = {"image": "red", "text": "blue", "icon": "green"}
            color_mapping_prompt = {"image": "red", "icon": "green"}
            image_debug, image_prompt, list_of_text = self.parser_to_prompt(image, regions, color_mapping_debug, color_mapping_prompt) # full set-of-marks drawing w/ visibility filtering, overlap detection, and colors
            logs['foreground_window_regions'] = image_debug
            logs['foreground_window_prompt'] = image_prompt
            # --------------------------------
            # --------------------------------

            # construct prompt
            prev_actions_str = prev_actions_to_string(self.prev_actions, self.n_prev)

            logs['window_title'] = window_title
            logs['window_names_str'] = window_names_str
            logs['computer_clipboard'] = computer_clipboard
            logs['image_width'] = image.width
            logs['image_height'] = image.height
            logs['regions'] = regions

            user_question = build_user_msg_visual(instruction, window_title, window_names_str, computer_clipboard, rendering, list_of_text, prev_actions_str, self.memory_block_text)
            logs['user_question'] = user_question
            
            image_resized, w_resized, h_resized, factor = resize_image_openai(view_image)
            image_prompt_resized, w_resized, h_resized, factor = resize_image_openai(image_prompt)
            
            image_prompts = [image_resized, image_prompt_resized]
            if self.use_last_screen:
                last_image = self.last_image if self.last_image is not None else image_resized
                self.last_image = image_resized
                logs['last_image'] = last_image
                
                #image_prompts = [last_image] + image_prompts
                image_prompts = [last_image, image_prompt_resized]

            # send to gpt
            logger.info("Thinking...")
            print("Calling GPT")
            plan_result = self.llm_client.plan(image_prompts, user_question)
            print("GPT responded")

        logs['plan_result'] = plan_result

        # extract the textual memory block
        memory_block = re.search(r'```memory\n(.*?)```', plan_result, re.DOTALL)
        if memory_block:
            self.memory_block_text = '```memory\n' + memory_block.group(1) + '```'

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

        self.prev_actions.append(code_block_text)
        scale = (original_w/w, original_h/h)

        response = ""
        computer_update_args = {
            'rects': rects,
            'window_rect': view_rect,
            'screenshot': view_image,
            'scale': scale,
            'clipboard_content': computer_clipboard,
            'swap_ctrl_alt': False
        }

        self.step_counter += 1

        # actions = code_block.split("\n")
        # remove empty lines and comments
        # actions = [action for action in actions if action.strip() and not action.strip().startswith("#")]

        # extract the high-level decision block
        decision_block = re.search(r'```decision\n(.*?)```', plan_result, re.DOTALL)
        if decision_block:
            self.decision_block_text = decision_block.group(1)
            if "DONE" in self.decision_block_text:
                actions = ["DONE"]
            elif "FAIL" in self.decision_block_text:
                actions = ["FAIL"]
            elif "WAIT" in self.decision_block_text:
                actions = ["WAIT"]

        return response, actions, logs, computer_update_args


    def reset(self):
        self.memory_block_text = self.memory_block_text_empty
        self.prev_actions = []
        self.clipboard_content = None
        self.step_counter = 0
        self.last_image = None