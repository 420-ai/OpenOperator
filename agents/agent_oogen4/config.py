import os
import json

class ConfigObject:
    """Helper class to convert a dictionary into an object with attribute access."""
    def __init__(self, dictionary):
        for key, value in dictionary.items():
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
        """Convert the ConfigObject instance back to a dictionary recursively."""
        result = {}
        for key, value in self.__dict__.items():
            result[key] = value._to_dict() if isinstance(value, ConfigObject) else value
        return result

    def __getitem__(self, key):
        """Enable dictionary-like access."""
        return getattr(self, key)

    def __repr__(self):
        return str(self.__dict__)

class OOConfig:
    def __init__(self):
        self.config = ConfigObject({})  # Initialize with an empty config object

    def load(self, domain: str, scenario: str):
        config_path = os.path.join(os.path.dirname(__file__), "configs", domain, f"{scenario}.json")

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
