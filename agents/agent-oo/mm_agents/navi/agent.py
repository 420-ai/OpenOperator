import json
import logging
from pprint import pprint
import re
from typing import Dict, List
# from mm_agents.planner.computer import Computer, WindowManager
from mm_agents.navi.gpt.gpt4v_planner import GPT4V_Planner
from mm_agents.navi.gpt import planner_messages
import copy
from io import BytesIO
from my_utils import save_to_json, save_base64_to_png
# Full client - OLD
# from mm_agents.navi.screenparsing_oss.omniparser.omniparser import Omniparser
# HTTP client - NEW
from mm_agents.navi.screenparsing_oss.omniparser_client.omniparser import Omniparser


logger = logging.getLogger("desktopenv.agent")

def remove_min_leading_spaces(text):  
    lines = text.split('\n')  
    min_spaces = min(len(line) - len(line.lstrip(' ')) for line in lines if line)  
    return '\n'.join([line[min_spaces:] for line in lines])  

def prev_actions_to_string(prev_actions, n_prev=3):  
    result = ""  
    n_prev = min(n_prev, len(prev_actions))  # Limit n_prev to the length of the array  
    for i in range(1, n_prev + 1):  
        action = prev_actions[-i]  # Get the element at index -i (from the end)  
        result += f"Screen is currently at time step T. Below is the action executed at time step T-{i}: \n{action}\n\n"  
    return result  

from PIL import Image

def resize_image_openai(image):
    """
    Resize the image to OpenAI's input resolution so that text written on it doesn't get processed any further.
    
    Steps:
    1. If the image's largest side is greater than 2048, scale it down so that the largest side is 2048, maintaining aspect ratio.
    2. If the shortest side of the image is longer than 768px, scale it so that the shortest side is 768px.
    3. Return the resized image.
    
    Reference: https://platform.openai.com/docs/guides/vision/calculating-costs
    """
    max_size = 2048
    target_short_side = 768
    
    out_w, out_h = image.size

    # Step 0: return the image without scaling if it's already within the target resolution
    if out_w <= max_size and out_h <= max_size and min(out_w, out_h) <= target_short_side:
        return image, out_w, out_h, 1.0
    
    # Initialize scale_factor
    scale_factor = 1.0
    
    # Step 1: Calculate new size to fit within a 2048 x 2048 square
    max_dim = max(out_w, out_h)
    if max_dim > max_size:
        scale_factor = max_size / max_dim
        out_w = int(out_w * scale_factor)
        out_h = int(out_h * scale_factor)
    
    # Step 2: Calculate new size if the shortest side is longer than 768px
    min_dim = min(out_w, out_h)
    if min_dim > target_short_side:
        new_scale_factor  = target_short_side / min_dim
        out_w = int(out_w * new_scale_factor)
        out_h = int(out_h * new_scale_factor)
        # Combine scale factors from both steps
        scale_factor *= new_scale_factor
    
    # Perform the resize operation once
    resized_image = image.resize((out_w, out_h))
    
    return resized_image, out_w, out_h, scale_factor

class NaviAgent:
    def __init__(
            self,
            server: str = "azure",
            model: str = "gpt-4o", # openai or "phi3-v"
            som_config = None,
            som_origin = "oss", # "oss", "a11y", "mixed-oss", "omni", "mixed-omni"
            obs_view = "screen", # "screen" or "window"
            auto_window_maximize = False,
            use_last_screen = True,
            temperature: float = 0.5,
    ):
        self.action_space = "code_block"
        self.server = server
        self.model = model
        self.som_origin = som_origin
        self.som_config = som_config
        self.obs_view = obs_view
        self.auto_window_maximize = auto_window_maximize
        self.prev_window_title = None
        self.prev_window_rect = None
        self.last_image = None
        self.use_last_screen = use_last_screen

        # hard-coded params
        device = "cpu"
        self.h, self.w = 1200, 1920 
        
        self.omni_proposal = Omniparser()

        self.gpt4v_planner = GPT4V_Planner(server=self.server, model=self.model, temperature=temperature)
        if use_last_screen:
            self.gpt4v_planner.system_prompt = planner_messages.planning_system_message_shortened_previmg
        
        from mm_agents.navi.screenparsing_oss.utils.obs import parser_to_prompt
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
        
        if self.obs_view == "screen":
            image_file = BytesIO(obs['screenshot'])
            view_image = Image.open(image_file)
            view_rect = [0, 0, view_image.width, view_image.height]
        else:
            view_image = obs['window_image']
            view_rect = obs['window_rect']
        
        window_title, window_names_str, window_rect, computer_clipboard = obs['window_title'], obs['window_names_str'], obs['window_rect'], obs['computer_clipboard']
        original_h, original_w = view_image.height, view_image.width
        
        override_plan = False
        
        # if the window is different, maximize it
        if self.auto_window_maximize:
            # when we call .maximize(), windows switches to a overflow window for 1 step, so we need to ignore it
            if "System tray" not in window_title and "Defender" not in window_title:
                if window_title != self.prev_window_title and window_rect != self.prev_window_rect:
                    # debug logging {{{
                    logs['window_title'] = window_title
                    logs['window_rect'] = window_rect
                    logs['prev_window_title'] = self.prev_window_title
                    logs['prev_window_rect'] = self.prev_window_rect
                    # }}} debug logging
                    self.prev_window_title = window_title
                    self.prev_window_rect = window_rect
                    code_result = "\n".join([
                        "# forcing step to execute auto_window_maximize...",
                        "computer.os.maximize_window()"
                    ])
                    plan_result = f"```python\n{code_result}\n```"
                    w, h = original_w, original_h
                    rects = []
                    override_plan = True
                
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
            regions = self.omni_proposal.propose_ents(image, with_captions=True)

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

            user_question = planner_messages.build_user_msg_visual(instruction, window_title, window_names_str, computer_clipboard, rendering, list_of_text, prev_actions_str, self.memory_block_text)
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
            plan_result = self.gpt4v_planner.plan(image_prompts, user_question)
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
        self.prev_window_title = None
        self.prev_window_rect = None
        self.clipboard_content = None
        self.step_counter = 0
        self.last_image = None