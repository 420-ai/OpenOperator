import os
import json

class OOConfig:
    def __init__(self):
        self.config = {}

    def load(self, domain: str, scenario: str):
        print(os.getcwd())
        config_path = os.path.join(os.getcwd(), "configs", domain, f"{scenario}.json")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = json.load(file)

    @property
    def value(self) -> dict:
        return self.config

    @property
    def instruction(self) -> str:
        return self.config.get("instruction", "")
    
    @property
    def SYSTEM_MESSAGE(self) -> str:
        return self._get_nested_value_as_string("messages.SYSTEM_MESSAGE")

    @property
    def USER_MESSAGE(self) -> str:
        return self._get_nested_value_as_string("messages.USER_MESSAGE")

    @property
    def PARSED_UI_ELEMENTS_MESSAGE(self) -> str:
        return self._get_nested_value_as_string("messages.PARSED_UI_ELEMENTS_MESSAGE")

    def _get_nested_value_as_string(self, key_path: str, separator: str = "\n", default="") -> str:
        """Helper function to retrieve nested dictionary values and join lists into a string."""
        value = self._get_nested_value(key_path, default)
        if isinstance(value, list):
            return separator.join(value)
        return value if isinstance(value, str) else default

    def _get_nested_value(self, key_path: str, default=None):
        """Helper function to retrieve nested dictionary values using dot notation."""
        keys = key_path.split(".")
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value