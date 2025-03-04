from __future__ import annotations

import logging
import os
import time
from typing import Callable, Any, Optional
from typing import List, Dict, Union

import gymnasium as gym

# from desktop_env.evaluators import metrics, getters

from environment.computer.server_client import ServerClient

logger = logging.getLogger("environment.computer.env")


Metric = Callable[[Any, Any], float]
Getter = Callable[[gym.Env, Dict[str, Any]], Any]

class ComputerEnv(gym.Env):
    """
    ComputerEnv with OpenAI Gym interface. It provides a desktop environment for setting and evaluating desktop automation tasks.
    """

    def __init__(
            self,
            action_space: str = "computer_13", # "computer_13", "pyautogui", "code_block"
            emulator_ip: str = "127.0.0.1",
            emulator_port: int = 5000
    ):
        # Initialize emulator and controller
        logger.info("Initializing...")
        
        logger.info("Using external emulator...")
        self.remote_vm = True
        self.vm_ip = emulator_ip
        self.vm_port = emulator_port

        self.controller = ServerClient(vm_ip=self.vm_ip, vm_port=self.vm_port)
        
        # mode: human or machine
        self.instruction = None
        assert action_space in ["computer_13", "pyautogui", "code_block"]
        self.action_space = action_space

        # episodic stuffs, like counters, will be updated or reset
        # when calling self.reset()
        self._traj_no: int = -1
        self._step_no: int = 0
        self.action_history: List[Dict[str, any]] = []

    def reset(self, task_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        GYMNASIUM ENVIRONMENT INTERFACE
        Reset the environment and return the initial observation.
        """

        logger.info("Resetting environment...")

        logger.info("Setting counters...")
        self._traj_no += 1
        self._step_no = 0
        self.action_history.clear()

        time.sleep(5)

        logger.info("Starting emulator...")
        self._wait_emulator()
        logger.info("Emulator started.")

        if task_config is not None:
            logger.info("Setting task info...")
            self._set_task_info(task_config)

            # logger.info(f"TASK RESULT GETTER: {self.result_getter}")
            # logger.info(f"EXPECTED RESULT GETTER: {self.expected_getter}")
            # logger.info(f"TASK METRIC: {self.metric}")
            # logger.info(f"TASK EVALUATOR: {self.evaluator}")

            time.sleep(5)
            logger.info("Environment setup complete.")

        observation = self._get_obs()
        return observation

    def step(self, action, pause=0.5):
        """
        GYMNASIUM ENVIRONMENT INTERFACE
        Execute the action and return the next observation, reward, done, and info.
        """
        self._step_no += 1
        self.action_history.append(action)

        reward = 0  # todo: Define reward calculation for each example
        done = False  # todo: Define episode termination condition for each example
        info = {}
        # handle the special actions
        if action in ['WAIT', 'FAIL', 'DONE']:
            if action == 'WAIT':
                time.sleep(pause)
            elif action == 'FAIL':
                done = True
                info = {"fail": True}
            elif action == 'DONE':
                done = True
                info = {"done": True}
        else:
            if self.action_space == "computer_13":
                # the set of all possible actions defined in the action representation
                self.controller.execute_action(action)
            elif self.action_space == "pyautogui":
                if action in ['WAIT', 'FAIL', 'DONE']:
                    self.controller.execute_action(action)
                else:
                    # the set of all possible python commands insides `pyautogui`
                    self.controller.execute_python_command(action)
            elif self.action_space == "code_block":
                self.controller.execute_python_windows_command(action)
            else:
                raise ValueError("Unknown action space: {}".format(self.action_space))
        # wait a little before taking the next observation
        time.sleep(pause)
        observation = self._get_obs()

        return observation, reward, done, info

    def render(self, mode='human'):
        """
        GYMNASIUM ENVIRONMENT INTERFACE
        Render the environment.
        """
        logger.info("Rendering environment...")
        pass

    def close(self):
        """
        GYMNASIUM ENVIRONMENT INTERFACE
        Close the environment.
        """
        logger.info("Closing environment...")


    # -----------------------------------------
    # CUSTOM METHODS
    # -----------------------------------------

    @property
    def vm_platform(self):
        return self.controller.get_vm_platform()

    @property
    def vm_screen_size(self):
        return self.controller.get_vm_screen_size()

    def _wait_emulator(self):
        """
        Continuously calls `get_probe` until it returns True, indicating the VM is ready.
        Polls every 5 seconds up to a specified maximum retry limit.
        """
        max_attempts = 20
        attempt = 0

        while attempt < max_attempts:
            if self.controller.get_probe(): # Check if VM is ready
                logger.info("VM is up and ready.")
                return True
            
            logger.info("VM not ready yet. Retrying in 5 seconds...")
            time.sleep(5)  # Wait for 5 seconds before retrying
            attempt += 1

        logger.error("VM did not become ready after %d attempts.", max_attempts)
        return False

    def _get_screenshot(self):
        screenshot = None
        # Get the screenshot and save to the image_path
        max_retries = 20
        for _ in range(max_retries):

            try:

                # Replace VM QEMU screenshot with the one from the server
                # screenshot = self.vm_controller.take_screenshot()
                screenshot = self.controller.get_screenshot()

                os.makedirs("tmp", exist_ok=True)
                file_path = os.path.join("tmp", "screenshot.png")
                with open(file_path, "wb") as f:
                    f.write(screenshot)

                print("Screenshot saved")

                if screenshot is not None:
                    break
                print("Retrying to get screenshot...")
                time.sleep(1)

            except Exception as e:
                logger.error(f"Failed to get screenshot: {e}")
                time.sleep(1)

        if screenshot is None:
            logger.error("Failed to get screenshot!")

        return screenshot

    

    def evaluate(self):
        """
        Evaluate whether the task is successfully completed.
        """

        if self.evaluator['func'] == "infeasible":
            if len(self.action_history) > 0 and self.action_history[-1] == "FAIL":
                # logger.info("Infeasible task and last agent action = FAIL")
                return 1
            else:
                # logger.info("Infeasible task but last agent action != FAIL")
                return 0
        else:
            if len(self.action_history) > 0 and self.action_history[-1] == "FAIL":
                # logger.info("Feasible task but last agent = FAIL")
                return 0

        if type(self.metric) == list:
            results = []
            for idx, metric in enumerate(self.metric):
                try:
                    config = self.evaluator["result"][idx]
                    result_state = self.result_getter[idx](self, config)
                except FileNotFoundError:
                    logger.error("File not found!")
                    if self.metric_conj == 'and':
                        return 0

                expected = self.evaluator["expected"][idx]
                expected_state = self.expected_getter[idx](self, expected) if expected else None

                metric: int = metric(result_state, expected_state,
                                     **self.metric_options[idx]) if expected_state is not None \
                    else metric(result_state, **self.metric_options[idx])

                if self.metric_conj == 'and' and float(metric) == 0.0:
                    return 0
                elif self.metric_conj == 'or' and float(metric) == 1.0:
                    return 1
                else:
                    results.append(metric)
            return sum(results) / len(results) if self.metric_conj == 'and' else max(results)
        else:
            try:
                result_state = self.result_getter(self, self.evaluator["result"])
            except FileNotFoundError:
                logger.error("File not found!")
                return 0
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                return 0
            expected_state = self.expected_getter(self, self.evaluator["expected"]) if "expected" in self.evaluator \
                else None
 
            # logger.info(f"RESULT STATE: {result_state}")
            # logger.info(f"EXPECTED STATE: {expected_state}")

            metric: float = self.metric(result_state, expected_state,
                                        **self.metric_options) if expected_state is not None \
                else self.metric(result_state, **self.metric_options)
            
        if isinstance(metric, (float, int, bool)):
            return metric
        else:
            logger.error("Task metric value produced is neither numeric nor boolean: returning 0 instead")
            return 0            

        return metric
    
    def _set_task_info(self, task_config: Dict[str, Any]):
        """
        Set task information from the task configuration.
        """
        self.task_id: str = task_config["id"]
        self.cache_dir: str = os.path.join(self.cache_dir_base, self.task_id)
        os.makedirs(self.cache_dir, exist_ok=True)
        self.instruction = task_config["instruction"]
        self.config = task_config["config"] if "config" in task_config else []

        # evaluator dict
        # func -> metric function string, or list of metric function strings
        # conj -> conjunction of multiple metrics if func is a list with length > 1, "and"/"or"
        # result -> result getter config, or list of result getter configs
        # expected (optional) -> expected getter config, or list of expected getter configs
        # options (optional) -> metric options, or list of metric options
        # if func is a str list, then result, expected (if exists), options (if exists) should also be lists of the same length
        # even if one of the metrics does not need expected or options field, it should be included in the list with None
        self.evaluator = task_config["evaluator"]
        # self.metric: Metric = [getattr(metrics, func) for func in self.evaluator["func"]] \
        #     if isinstance(self.evaluator["func"], list) \
        #     else getattr(metrics, self.evaluator["func"])
        # self.metric_conj: str = self.evaluator.get("conj", "and")  # take conjunction of multiple metrics
        # if "result" in self.evaluator and len(self.evaluator["result"]) > 0:
        #     self.result_getter: Getter = [getattr(getters, "get_{:}".format(res["type"])) for res in
        #                                   self.evaluator["result"]] \
        #         if isinstance(self.evaluator["result"], list) \
        #         else getattr(getters, "get_{:}".format(self.evaluator["result"]["type"]))
        # else:
        #     self.result_getter = [None] * len(self.metric) \
        #         if isinstance(self.metric, list) \
        #         else None

        # if "expected" in self.evaluator and len(self.evaluator["expected"]) > 0:
        #     self.expected_getter: Getter = [getattr(getters, "get_{:}".format(exp["type"])) if exp else None for exp in
        #                                     self.evaluator["expected"]] \
        #         if isinstance(self.evaluator["expected"], list) \
        #         else getattr(getters, "get_{:}".format(self.evaluator["expected"]["type"]))
        # else:
        #     self.expected_getter = [None] * len(self.metric) \
        #         if isinstance(self.metric, list) \
        #         else None
        # self.metric_options: Union[List[Dict[str, Any]], Dict[str, Any]] = [opt if opt else {} for opt in
        #                                                                     self.evaluator["options"]] \
        #     if isinstance(self.evaluator.get("options", {}), list) \
        #     else self.evaluator["options"] \
        #     if "options" in self.evaluator \
        #     else [{}] * len(self.metric) \
        #     if isinstance(self.metric, list) \
        #     else {}

        # assert (not isinstance(self.evaluator["func"], list)
        #         or (len(self.metric) == len(self.result_getter) == len(self.expected_getter) == len(
        #             self.metric_options)))


    def _get_obs(self):
        screenshot = self._get_screenshot()
        # screenshot = None
        # print("screenshot done")
        accessibility_tree = self.controller.get_accessibility_tree(backend=self.a11y_backend) if self.require_a11y_tree else None
        # accessibility_tree = "test"
        # accessibility_tree = None
        # print("accessibility_tree done")
        terminal = self.controller.get_terminal_output() if self.require_terminal else None
        # terminal = None
        obs = self.controller.get_obs_winagent()
        if obs is not None:
            window_image, window_title, window_rect, window_names_str, computer_clipboard, human_input = obs
            return {
                "screenshot": screenshot,
                "accessibility_tree": accessibility_tree,
                "terminal": terminal,
                "instruction": self.instruction,
                "window_title": window_title,
                "window_rect": window_rect,
                "window_image": window_image,
                "window_names_str": window_names_str,
                "computer_clipboard": computer_clipboard,
                "human_input": human_input
                }
        else:
            return None
        # print("terminal done")
        # print("LOG: Observation collected")
    