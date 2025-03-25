import os
from typing import Any, Dict, List, Optional
from PIL import Image
import json
from core.config import OOConfig

class State:
    """
    Manages application state on the file system.
    Each run of the application uses a different subfolder with timestamp.
    """
    
    def __init__(self, dir: str, timestamp: str):
        """
        Initialize the State object.
        """

        self.base_dir = os.path.join(dir, "state")
        # Create a timestamp-based run directory
        self.run_dir = os.path.join(self.base_dir, timestamp)
        os.makedirs(self.run_dir, exist_ok=True)
        
        # Keep track of the current plan version
        self.current_plan_version = None
        self.current_iteration = None
    
    # ----------------------------------------------------
    # General management
    # ----------------------------------------------------

    # Config
    def save_config(self, config: OOConfig) -> None:
        with open(os.path.join(self.run_dir, "config.json"), "w", encoding="utf-8") as f:
            json.dump(config.config._to_dict(), f, indent=4)  

    def get_config(self) -> OOConfig:
        with open(os.path.join(self.run_dir, "config.json"), "r", encoding="utf-8") as f:
            config_dict = json.load(f)

        return OOConfig(config_dict)

    # Environment
    def save_initial_observation(self, observation: Dict[str, Any]) -> str:
        env_dir = os.path.join(self.run_dir, f"environment")
        os.makedirs(env_dir, exist_ok=True)

        # Save the screenshot
        observation["screenshot"].save(os.path.join(env_dir, "screenshot.png"))
        # Save the ui elements
        with open(os.path.join(env_dir, "ui_elements.json"), "w") as f:
            json.dump(observation["ui_elements"], f, indent=4)

    # Task
    def save_task_result(self, task_result: str): 
        with open(os.path.join(self.run_dir, "task_result.txt"), "w") as f:
            f.write(task_result)
        

    # ----------------------------------------------------
    # Plan version management
    # ----------------------------------------------------

    def create_new_plan_version(self) -> str:
        """
        Create a new plan version directory with an incremented version number.
        
        Returns:
            Path to the new plan version directory
        """
        if self.current_plan_version is None:
            new_version = 0
        else:
            # LK TODO: Double-check the versions
            latest_version = self.get_latest_plan_version()
            if self.current_plan_version != latest_version:
                raise ValueError("Something is wrong - Current plan version does not match the latest version")

            new_version = self.current_plan_version + 1

        plan_dir = os.path.join(self.run_dir, f"plan_v{new_version}")
        os.makedirs(plan_dir, exist_ok=True)
        self.current_plan_version = new_version
        return plan_dir
    
    def _get_plan_version_dir(self, version: Optional[int] = None) -> str:
        """
        Get the directory path for a plan version.
        
        Args:
            version: Plan version number, uses current if None
            
        Returns:
            Path to the plan version directory
        """
        if version is None:
            if self.current_plan_version is None:
                raise ValueError("No plan version selected")
            version = self.current_plan_version
        
        return os.path.join(self.run_dir, f"plan_v{version}")
    
    def save_plan_text(self, content: str, version: Optional[int] = None) -> str:
        """
        Save plan text content to plan.txt.
        
        Args:
            content: Text content to save
            version: Plan version number, uses current if None
            
        Returns:
            Path to the saved file
        """
        plan_dir = self._get_plan_version_dir(version)
        file_path = os.path.join(plan_dir, "plan.txt")
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def save_plan_image(self, image: Image.Image, image_name: str, version: Optional[int] = None) -> str:
        """
        Save a PIL Image to the plan version directory.
        
        Args:
            image: PIL Image object to save
            image_name: Name to save the image as (e.g., "t0.png")
            version: Plan version number, uses current if None
            
        Returns:
            Path to the saved image
        """
        plan_dir = self._get_plan_version_dir(version)
        dest_path = os.path.join(plan_dir, image_name)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        # Save the image
        image.save(dest_path)
        return dest_path
    
    def save_plan_result(self, content: str, version: Optional[int] = None) -> str:
        """
        Save plan result content to plan_result.txt.
        
        Args:
            content: Result content to save
            version: Plan version number, uses current if None
        Returns:
            Path to the saved file
        """
        plan_dir = self._get_plan_version_dir(version)
        file_path = os.path.join(plan_dir, "plan_result.txt")
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def list_plan_versions(self) -> List[str]:
        """
        List all plan versions in the current run.
        
        Returns:
            List of plan version directories
        """
        if not os.path.exists(self.run_dir):
            return []
        
        versions = [d for d in os.listdir(self.run_dir) if d.startswith("plan_v") and os.path.isdir(os.path.join(self.run_dir, d))]
        versions.sort(key=lambda v: int(v.split("_v")[1]))
        return versions
    
    def get_latest_plan_version(self) -> Optional[int]:
        """
        Get the latest plan version number.
        
        Returns:
            Latest plan version number or None if no versions exist
        """
        versions = self.list_plan_versions()
        if not versions:
            return None
        
        version_numbers = [int(v.split("_v")[1]) for v in versions]
        return max(version_numbers)
    

    # ----------------------------------------------------
    # Plan step management
    # ----------------------------------------------------

    def _get_plan_step_dir(self, version: Optional[int] = None) -> str:
        """
        Get the directory path for a plan step.
        
        Args:
            version: Plan version number, uses current if None
            
        Returns:
            Path to the plan step directory
        """
        plan_dir = self._get_plan_version_dir(version)
        return os.path.join(plan_dir, "plan_step")
    
    def save_plan_step_text(self, content: str, version: Optional[int] = None) -> str:
        """
        Save plan step text content to plan_step.txt.
        
        Args:
            content: Text content to save
            version: Plan version number, uses current if None
            
        Returns:
            Path to the saved file
        """
        plan_step_dir = self._get_plan_step_dir(version)
        os.makedirs(plan_step_dir, exist_ok=True)
        file_path = os.path.join(plan_step_dir, "plan_step.txt")
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def save_plan_step_result(self, content: str, version: Optional[int] = None) -> str:
        """
        Save plan step result content to plan_step_result.txt.
        
        Args:
            content: Result content to save
            version: Plan version number, uses current if None
            
        Returns:
            Path to the saved file
        """
        plan_step_dir = self._get_plan_step_dir(version)
        os.makedirs(plan_step_dir, exist_ok=True)
        file_path = os.path.join(plan_step_dir, "plan_step_result.txt")
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    

    # ----------------------------------------------------
    # Plan step - iteration - management
    # ----------------------------------------------------

    def create_iteration(self, iteration_number: int, version: Optional[int] = None) -> str:
        """
        Create an iteration directory for a plan step.
        
        Args:
            iteration_number: Iteration number (1, 2, etc.)
            version: Plan version number, uses current if None
            
        Returns:
            Path to the iteration directory
        """
        plan_step_dir = self._get_plan_step_dir(version)
        os.makedirs(plan_step_dir, exist_ok=True)
        
        iteration_dir = os.path.join(plan_step_dir, f"iteration_{iteration_number}")
        os.makedirs(iteration_dir, exist_ok=True)

        self.current_iteration = iteration_number
        return iteration_dir
    
    def _get_iteration_dir(self, iteration_number: Optional[int] = None, version: Optional[int] = None) -> str:
        """
        Get the directory path for an iteration.
        
        Args:
            iteration_number: Iteration number, uses current if None
            version: Plan version number, uses current if None
            
        Returns:
            Path to the iteration directory
        """
        if iteration_number is None:
            if self.current_iteration is None:
                raise ValueError("No iteration selected")
            else:
                iteration_number = self.current_iteration
        
        plan_step_dir = self._get_plan_step_dir(version)
        return os.path.join(plan_step_dir, f"iteration_{iteration_number}")
    
    def save_iteration_actions(self, content: str, iteration_number: Optional[int] = None, version: Optional[int] = None) -> str:
        """
        Save iteration actions content to actions.txt.
        
        Args:
            content: Actions content to save
            iteration_number: Iteration number, uses current if None
            version: Plan version number, uses current if None
            
        Returns:
            Path to the saved file
        """
        iteration_dir = self._get_iteration_dir(iteration_number, version)
        os.makedirs(iteration_dir, exist_ok=True)
        file_path = os.path.join(iteration_dir, "actions.txt")
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def _create_iteration_validation_dir(self, iteration_number: Optional[int] = None, version: Optional[int] = None) -> str:
        """
        Create a validation directory for an iteration.
        
        Args:
            iteration_number: Iteration number, uses current if None
            version: Plan version number, uses current if None
            
        Returns:
            Path to the validation directory
        """
        iteration_dir = self._get_iteration_dir(iteration_number, version)
        os.makedirs(iteration_dir, exist_ok=True)
        
        validation_dir = os.path.join(iteration_dir, "validation")
        os.makedirs(validation_dir, exist_ok=True)
        return validation_dir
    
    def save_iteration_validation_result(self, content: str, iteration_number: Optional[int] = None, version: Optional[int] = None) -> str:
        """
        Save validation result content to result.txt.
        
        Args:
            content: Result content to save
            iteration_number: Iteration number, uses current if None
            version: Plan version number, uses current if None
            
        Returns:
            Path to the saved file
        """
        validation_dir = self._create_iteration_validation_dir(iteration_number, version)
        file_path = os.path.join(validation_dir, "result.txt")
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def save_iteration_validation_image(self, image: Image.Image, image_name: str, iteration_number: Optional[int] = None, version: Optional[int] = None) -> str:
        """
        Save a PIL Image to the validation directory.
        
        Args:
            image: PIL Image object to save
            image_name: Name to save the image as (e.g., "t1.png")
            iteration_number: Iteration number, uses current if None
            version: Plan version number, uses current if None
            
        Returns:
            Path to the saved image
        """
        validation_dir = self._create_iteration_validation_dir(iteration_number, version)
        dest_path = os.path.join(validation_dir, image_name)
        
        # Save the image
        image.save(dest_path)
        return dest_path
    

    # ----------------------------------------------------
    # Get data
    # ----------------------------------------------------

    def _list_images(self, directory: str) -> List[str]:
        """
        List all image files in a directory.
        
        Args:
            directory: Path to the directory to search for images.
        
        Returns:
            A list of image file paths.
        """
        if not os.path.exists(directory):
            return []

        return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('.png', '.jpg', '.jpeg'))]

    @property
    def current_plan_data(self) -> Dict[str, Optional[str]]:
        """
        Retrieve the current plan data including text, validation, images, and plan step data.
        
        Returns:
            A dictionary containing:
            - "plan_text": Content of plan.txt
            - "plan_validation": Content of plan_validation.txt
            - "images": List of image file paths in the plan directory
            - "plan_step": A collection of plan step data, including all iterations
        """
        if self.current_plan_version is None:
            raise ValueError("No plan version selected")

        plan_dir = self._get_plan_version_dir(self.current_plan_version)
        
        plan_text_path = os.path.join(plan_dir, "plan.txt")
        validation_text_path = os.path.join(plan_dir, "plan_validation.txt")

        data = {
            "plan_text": None,
            "plan_validation": None,
            "images": self._list_images(plan_dir),
            "plan_step": {
                "text": None,
                "result": None,
                "iterations": []
            }
        }

        if os.path.exists(plan_text_path):
            with open(plan_text_path, "r") as f:
                data["plan_text"] = f.read()

        if os.path.exists(validation_text_path):
            with open(validation_text_path, "r") as f:
                data["plan_validation"] = f.read()

        # Get plan step data including all iterations
        plan_step_dir = os.path.join(plan_dir, "plan_step")
        if os.path.exists(plan_step_dir):

            # Plan step text
            plan_step_text_path = os.path.join(plan_step_dir, "plan_step.txt")
            if os.path.exists(plan_step_text_path):
                with open(plan_step_text_path, "r") as f:
                    data["plan_step"]["text"] = f.read()

            # Plan step result
            plan_step_result_path = os.path.join(plan_step_dir, "plan_step_result.txt")
            if os.path.exists(plan_step_result_path):
                with open(plan_step_result_path, "r") as f:
                    data["plan_step"]["result"] = f.read()

            # List all iterations in the plan step
            data["plan_step"]["iterations"] = self.get_current_plan_step_iterations_data()

        return data

    def get_current_plan_step_iterations_data(self) -> List[Dict[str, Optional[str]]]:
        """
        Retrieve data for all iterations within the current plan step.
        
        Returns:
            A list of dictionaries, each representing an iteration with:
            - "iteration_number": The iteration number
            - "iteration_actions": The content of actions.txt
            - "validation_result": The content of result.txt in the validation folder
            - "images": List of image file paths in the iteration directory
        """
        if self.current_plan_version is None:
            raise ValueError("No plan version selected")

        plan_dir = self._get_plan_version_dir(self.current_plan_version)

        plan_step_dir = os.path.join(plan_dir, "plan_step")

        iterations_data = []
        
        # Loop through all iteration directories
        for iteration_folder in sorted(os.listdir(plan_step_dir)):
            if iteration_folder.startswith("iteration_"):
                iteration_number = int(iteration_folder.split("_")[1])
                iteration_dir = os.path.join(plan_step_dir, iteration_folder)
                validation_dir = os.path.join(iteration_dir, "validation")
                
                iteration_data = {
                    "iteration_number": iteration_number,
                    "iteration_actions": None,
                    "validation_result": None,
                    "validation_images": self._list_images(validation_dir)
                }

                # Iteration actions
                actions_path = os.path.join(iteration_dir, "actions.txt")
                if os.path.exists(actions_path):
                    with open(actions_path, "r") as f:
                        iteration_data["iteration_actions"] = f.read()

                # Validation result folder
                validation_result_path = os.path.join(validation_dir, "result.txt")
                if os.path.exists(validation_result_path):
                    with open(validation_result_path, "r") as f:
                        iteration_data["validation_result"] = f.read()

                iterations_data.append(iteration_data)

        return iterations_data
    
    def get_current_plan_image(self, image_name: str) -> Optional[Image.Image]:
        """
        Retrieve a specific image from the current plan version.
        
        Args:
            image_name: Name of the image file (e.g., "t0.png")
            
        Returns:
            PIL Image object or None if not found
        """
        plan_dir = self._get_plan_version_dir(self.current_plan_version)
        image_path = os.path.join(plan_dir, f"{image_name}.png")
        
        if os.path.exists(image_path):
            return Image.open(image_path)
        
        return None

    def get_all_plan_versions_data(self) -> Dict[str, Dict[str, Optional[str]]]:
        """
        Retrieve data for all plan versions including plan step text and result.
        
        Returns:
            A dictionary where the keys are plan version numbers and the values are dictionaries
            containing:
                - "plan_step_text": The content of plan_step.txt
                - "plan_step_result": The content of plan_step_result.txt
        """
        # Prepare a dictionary to store plan version data
        all_versions_data = {}

        # List all plan versions
        plan_versions = self.list_plan_versions()

        for version in plan_versions:
            version_number = int(version.split("_v")[1])  # Extract the version number

            # Get the directory for this plan version
            plan_version_dir = self._get_plan_version_dir(version_number)

            plan_step_data = {
                "plan_step_text": None,
                "plan_step_result": None
            }

            # Get plan step text
            plan_step_text_path = os.path.join(plan_version_dir, "plan_step", "plan_step.txt")
            if os.path.exists(plan_step_text_path):
                with open(plan_step_text_path, "r") as f:
                    plan_step_data["plan_step_text"] = f.read()

            # Get plan step result
            plan_step_result_path = os.path.join(plan_version_dir, "plan_step", "plan_step_result.txt")
            if os.path.exists(plan_step_result_path):
                with open(plan_step_result_path, "r") as f:
                    plan_step_data["plan_step_result"] = f.read()

            # Add plan step data for this version to the result dictionary
            all_versions_data[f"v{version_number}"] = plan_step_data

        return all_versions_data
