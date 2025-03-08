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