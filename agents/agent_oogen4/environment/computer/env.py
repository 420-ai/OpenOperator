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

logger = logging.getLogger("environment.computer")

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

        # Action space: click by element ID, type by element ID
        self.action_space = gym.spaces.Tuple((
            gym.spaces.Discrete(2),  # 0: Click, 1: Type
            gym.spaces.Discrete(100)  # UI Element ID (up to 100 recognized elements)
        ))

        self.config = config
        self.state = state
        self.tracker = tracker

        self.computer = computer
        self.som = omniparser

        # Server URLs
        self.ccs_url = "http://windows-vm:5000"  # CCS API for executing actions
        self.som_url = "http://windows-vm:6000/detect"  # SoM API for UI detection

        self.current_ui_elements = []  # Stores latest detected UI elements

    def step(self, action):
        """
        Executes an action: Click or Type into a UI element.
        """
        action_type, element_id = action
        element = self.get_element_by_id(element_id)

        if not element:
            reward = -1  # Invalid action penalty
            return self.get_observation(), reward, False, {}

        if action_type == 0:  # Click UI Element
            data = {"action": "click", "x": element["x"], "y": element["y"]}
        elif action_type == 1:  # Type into UI Element
            data = {"action": "type", "x": element["x"], "y": element["y"], "text": "Hello, AI!"}

        response = requests.post(f"{self.ccs_url}/execute", json=data)
        success = response.status_code == 200

        # Get updated observation
        screenshot, ui_elements = self.get_screenshot_and_ui()
        self.current_ui_elements = ui_elements

        # Reward Function (Example: reward clicking a UI button)
        reward = 1 if success else -1
        done = reward > 0  # End episode if a successful UI interaction happens

        return {"screenshot": screenshot, "ui_elements": self.get_ui_ids()}, reward, done, {}

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



    def get_screenshot_and_ui(self):
        """
        Fetches a screenshot and detected UI elements using the SoM tool.
        """
        # Fetch screenshot
        screenshot_response = requests.get(f"{self.ccs_url}/screenshot")
        screenshot = np.asarray(bytearray(screenshot_response.content), dtype=np.uint8)
        # screenshot = cv2.imdecode(screenshot, cv2.IMREAD_COLOR)

        # Fetch UI Elements (structured labels)
        ui_response = requests.get(self.som_url)
        ui_elements = json.loads(ui_response.text) if ui_response.status_code == 200 else []

        return screenshot, ui_elements

    def get_element_by_id(self, element_id):
        """
        Retrieves UI element data (x, y coordinates) by ID.
        """
        if element_id < len(self.current_ui_elements):
            return self.current_ui_elements[element_id]
        return None

    def get_ui_ids(self):
        """
        Returns a list of UI element IDs detected in the environment.
        """
        return list(range(len(self.current_ui_elements)))

    
