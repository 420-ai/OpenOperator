from typing import Tuple
import gymnasium as gym
import numpy as np
import requests
import json
from config import OOConfig
from state import State
from tracker import Tracker
from clients.computer import computer
from clients.som import omniparser
from functions import FUNCTIONS
import logging
import sys
from environment.computer.tools.keyboard_type import keyboard_type
from environment.computer.tools.keyboard_hotkeys import keyboard_hotkeys
from environment.computer.tools.mouse_move import mouse_move
from environment.computer.tools.mouse_scroll import mouse_scroll
from environment.computer.tools.mouse_left_click import mouse_left_click
from environment.computer.tools.mouse_double_click import mouse_double_click
import asyncio

logger = logging.getLogger("environment.computer")

async def async_tool_run(tool, params_json):
    """Runs tool.run asynchronously"""
    return await tool.run(args=params_json, cancellation_token=None)

class ComputerEnv(gym.Env):
    """
    Gymnasium environment for controlling a Windows 11 VM.
    - Uses Computer Control Server for execution.
    - Uses Omniparser (SoM = Set-of-Mark) tool for structured UI interaction.
    - Supports Plan-Execute-Inspect-Improve loop for RL.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(self, config: OOConfig, state: State, tracker: Tracker):
        # Observation space (parsed screenshot + structured UI elements)
        self.observation_space = gym.spaces.Dict({
            "screenshot": gym.spaces.Box(low=0, high=255, shape=(1080, 1920, 3), dtype=np.uint8),
            "ui_elements": gym.spaces.MultiDiscrete([100])  # Up to 100 labeled UI elements
        })

        # ??? Is this correct?

        # gym.spaces.Text = np.array("test string", dtype=np.object_)
        self.action_space = gym.spaces.Tuple((
            gym.spaces.Text(max_length=50), # Command for action
            gym.spaces.Text(max_length=500), # parameters for action
        ))

        self.config = config
        self.state = state
        self.tracker = tracker

        self.computer = computer
        self.som = omniparser

        self.tools = [
            keyboard_type,
            keyboard_hotkeys,
            mouse_move,
            mouse_scroll,
            mouse_left_click,
            mouse_double_click,
        ]

        # Server URLs
        # self.ccs_url = "http://windows-vm:5000"  # CCS API for executing actions
        # self.som_url = "http://windows-vm:6000/detect"  # SoM API for UI detection

        # self.current_ui_elements = []  # Stores latest detected UI elements

    def step(self, action: Tuple[str, str]):
        """
        Executes an action: Click or Type into a UI element.
        """

        # Enforce validation of action
        # if not self.action_space.contains(action):
        #     raise ValueError(f"Invalid action: {action}")


        action_type, params = action
        logger.debug(f"Action: {action_type}")
        logger.debug(f"Params: {params}")
    
        # Find the matching tool by name
        tool_selected = next((t for t in self.tools if t.__name__ == action_type), None)
        
        if not tool_selected:
            raise ValueError(f"Invalid action type: {action_type}")
        

        # print(type(params))

        params_json = json.loads(params)
        # print(type(params_json))

        # ----------------------------
        # Execute the action using the tool
        # ----------------------------

        tool_result = tool_selected(**params_json)

        # tool_result = async_tool_run(tool, params_json)
        # tool_result = await tool.run(args=params_json, cancellation_token=None)

        # tool_result = asyncio.run(tool.run(args=params_json, cancellation_token=None))

        # try:
        #     loop = asyncio.get_running_loop()  # Check if an event loop is already running
        #     task = loop.create_task(tool.run(args=params_json, cancellation_token=None))  # Schedule the async function
        #     tool_result = loop.run_until_complete(task)  # Wait for it to finish
        # except RuntimeError:  # If no loop is running, use asyncio.run()
        #     tool_result = asyncio.run(tool.run(args=params_json, cancellation_token=None))
        # ----------------------------
        # ----------------------------

        observation = ""
        reward = 0
        terminated = False # done
        truncated = False
        info = {
            "tool_result": tool_result,  # Result of the executed tool
        } # Contains auxiliary diagnostic information (helpful for debugging, learning, and logging).
    
        logger.debug(f"Observation: {observation}")
        logger.debug(f"Reward: {reward}")
        logger.debug(f"Terminated: {terminated}")
        logger.debug(f"Truncated: {truncated}")
        logger.debug(f"Info: {info}")

        return observation, reward, terminated, truncated, info

        # # Unpack action
        # action_type, element_id = action
        # element = self.get_element_by_id(element_id)

        # if not element:
        #     reward = -1  # Invalid action penalty
        #     return self.get_observation(), reward, False, {}

        # if action_type == 0:  # Click UI Element
        #     data = {"action": "click", "x": element["x"], "y": element["y"]}
        # elif action_type == 1:  # Type into UI Element
        #     data = {"action": "type", "x": element["x"], "y": element["y"], "text": "Hello, AI!"}

        # response = requests.post(f"{self.ccs_url}/execute", json=data)
        # success = response.status_code == 200

        # # Get updated observation
        # screenshot, ui_elements = self.get_screenshot_and_ui()
        # self.current_ui_elements = ui_elements

        # # Reward Function (Example: reward clicking a UI button)
        # reward = 1 if success else -1
        # done = reward > 0  # End episode if a successful UI interaction happens

        # return {"screenshot": screenshot, "ui_elements": self.get_ui_ids()}, reward, done, {}

    def reset(self):
        """
        Resets the environment (reloads VM snapshot).
        """

        # --------------------------------
        # Call Envrionment reset method
        start_functions = self.config.environment.start
        for item in start_functions:
            func_name = item["func"]  
            args = item.get("args", {})  
            if func_name in FUNCTIONS:
                if args:  
                    FUNCTIONS[func_name](**args)  
                else:
                    FUNCTIONS[func_name]()  
            else:
                print(f"Warning: Function '{func_name}' not found.")

        # --------------------------------
        # Get initial observation

        # 1. take a screenshot
        screenshot = self.computer.get_screenshot()
        # 2. analyze the screenshot with SoM
        parsed = self.som.analyze_image(screenshot)
        # 3. resize the screenshot
        screenshot_resized = parsed["parsed_image"].resize((1920, 1080))  

        # --------------------------------
        observation = {
            "screenshot": screenshot_resized,
            "ui_elements": parsed["parsed_content_list"]  
        }

        info = {}

        # region Log + State + Tracker
        logger.debug("Initial observation:", observation)
        self.state.save_initial_observation(observation)
        self.tracker.save("computer_env-reset", 
            [
                ("screenshot", observation["screenshot"]),
                ("ui_elements", observation["ui_elements"])
            ]
        )
        # endregion

        return observation, info

    def render(self, mode="human"):
        """
        Renders the current environment state.
        """
        pass

    def close(self):
        """
        Clean up resources.
        """
        pass



    # def get_screenshot_and_ui(self):
    #     """
    #     Fetches a screenshot and detected UI elements using the SoM tool.
    #     """
    #     # Fetch screenshot
    #     screenshot_response = requests.get(f"{self.ccs_url}/screenshot")
    #     screenshot = np.asarray(bytearray(screenshot_response.content), dtype=np.uint8)
    #     # screenshot = cv2.imdecode(screenshot, cv2.IMREAD_COLOR)

    #     # Fetch UI Elements (structured labels)
    #     ui_response = requests.get(self.som_url)
    #     ui_elements = json.loads(ui_response.text) if ui_response.status_code == 200 else []

    #     return screenshot, ui_elements

    # def get_element_by_id(self, element_id):
    #     """
    #     Retrieves UI element data (x, y coordinates) by ID.
    #     """
    #     if element_id < len(self.current_ui_elements):
    #         return self.current_ui_elements[element_id]
    #     return None

    # def get_ui_ids(self):
        # """
        # Returns a list of UI element IDs detected in the environment.
        # """
        # return list(range(len(self.current_ui_elements)))

    
