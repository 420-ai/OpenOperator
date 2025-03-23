import logging
from typing import Tuple
import gymnasium as gym
import numpy as np
import json
from core.clients.computer import ComputerClient
from core.clients.som import OmniparserClient
from core.state import State
from core.tracker import Tracker
from agent_oo4.environment.computer.tools.keyboard_type import keyboard_type
from agent_oo4.environment.computer.tools.keyboard_hotkeys import keyboard_hotkeys
from agent_oo4.environment.computer.tools.mouse_move import mouse_move
from agent_oo4.environment.computer.tools.mouse_scroll import mouse_scroll
from agent_oo4.environment.computer.tools.mouse_left_click import mouse_left_click
from agent_oo4.environment.computer.tools.mouse_double_click import mouse_double_click

logger = logging.getLogger("environment.computer")

class ComputerEnv(gym.Env):
    """
    Gymnasium environment for controlling a Windows 11 VM.
    - Uses Computer Control Server for execution.
    - Uses Omniparser (SoM = Set-of-Mark) tool for structured UI interaction.
    - Supports Plan-Execute-Inspect-Improve loop for RL.
    """

    name = "environment.computer"

    metadata = {"render_modes": ["human"]}

    def __init__(self, state: State, tracker: Tracker):
        # Observation space (parsed screenshot + structured UI elements)
        self.observation_space = gym.spaces.Dict({
            "screenshot": gym.spaces.Box(low=0, high=255, shape=(1080, 1920, 3), dtype=np.uint8),
            "ui_elements": gym.spaces.MultiDiscrete([100])  # Up to 100 labeled UI elements
        })

        self.action_space = gym.spaces.Tuple((
            gym.spaces.Text(max_length=50), # Command for action
            gym.spaces.Text(max_length=500), # parameters for action
        ))

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.computer = ComputerClient()
        self.som = OmniparserClient()

        self.step_count = 0

        self.tools = [
            keyboard_type,
            keyboard_hotkeys,
            mouse_move,
            mouse_scroll,
            mouse_left_click,
            mouse_double_click,
        ]

    def step(self, action: Tuple[str, str]):
        """
        Executes an action: Click or Type into a UI element.
        """
        self.step_count += 1
        logger.debug(f"\n***************************\nEnvironment step No.{self.step_count}\n***************************")

        action_type, params = action
        logger.debug(f"Action: {action_type}")
        logger.debug(f"Params: {params}")
    
        # Find the matching tool by name
        tool_selected = next((t for t in self.tools if t.__name__ == action_type), None)
        
        if not tool_selected:
            raise ValueError(f"Invalid action type: {action_type}")
        
        
        # ----------------------------
        # Execute the action using the tool functions
        # ----------------------------
        params_json = json.loads(params)
        tool_result = tool_selected(**params_json)
        # ----------------------------
        # ----------------------------

        # region Log + State + Tracker
        self.tracker.save(self.name, 
            [
                ("tool_result", tool_result),
            ]
        )
        # endregion

        observation = ""
        reward = 0
        terminated = False # done
        truncated = False
        info = {
            "tool_result": tool_result,  # Result of the executed tool
        } 
    
        logger.debug(f"Observation: {observation}")
        logger.debug(f"Reward: {reward}")
        logger.debug(f"Terminated: {terminated}")
        logger.debug(f"Truncated: {truncated}")
        logger.debug(f"Info: {info}")

        return observation, reward, terminated, truncated, info

    def reset(self):
        """
        Resets the environment (reloads VM snapshot).
        """
        self.step_count = 0

        
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
