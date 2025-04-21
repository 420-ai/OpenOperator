import os
import json

class ConfigObject:
    """Helper class to convert a dictionary into an object with attribute access."""
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            # Handle 'instruction' normalization here
            if key == "instruction" and isinstance(value, list):
                value = "\n".join(value)
            setattr(self, key, self._convert(value))

    def get(self, key, default=None):
        """Mimic dictionary get method, returning dictionary values as raw dicts."""
        value = getattr(self, key, default if default is not None else self.__dict__)
        return value._to_dict() if isinstance(value, ConfigObject) else value

    def _convert(self, value):
        """Recursively convert dictionaries into ConfigObject instances."""
        if isinstance(value, dict):
            return ConfigObject(value)
        elif isinstance(value, list):
            return [self._convert(item) if isinstance(item, dict) else item for item in value]
        return value

    def _to_dict(self):
        """Ensure full conversion of nested ConfigObject instances to dictionaries."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, ConfigObject):  # Ensure recursion
                result[key] = value._to_dict()
            elif isinstance(value, list):  # Handle lists of objects
                result[key] = [item._to_dict() if isinstance(item, ConfigObject) else item for item in value]
            else:
                result[key] = value
        return result

class OOConfig:
    def __init__(self, dictionary: dict = {}):
        self.config = ConfigObject(dictionary)  

    def load(self, domain: str, scenario: str):
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        PARENT_DIR = os.path.dirname(CURRENT_DIR)

        config_path = os.path.join(PARENT_DIR, "configs", domain, f"{scenario}.json")

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as file:
            self.config = ConfigObject(json.load(file))

    @property
    def value(self) -> dict:
        return self.config

    @property
    def instruction(self) -> str:
        return self.config.instruction

    @property
    def workflow(self):
        return self.config.workflow
    
    def model_config(self, name: str):
        models = self.config.workflow.models
        for model in models:
            if name.startswith(model.get("name")):
                return model
        raise ValueError(f"Model '{name}' not found in configuration.")

    @property
    def environment(self):
        return self.config.environment

    @property
    def evaluation(self):
        return self.config.evaluation
