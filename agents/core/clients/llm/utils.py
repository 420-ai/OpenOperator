from typing import List, Optional, Union
from core.models import Message
from datetime import datetime
import json
import os

# Load the LLM config once on import.
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "llm_config.json")
with open(CONFIG_PATH, "r") as f:
    LLM_CONFIG = json.load(f)

def calculate_cost_in_usd(provider: str, model_name: str, input_tokens: int, output_tokens: int) -> float:
    """
    Given a provider, model name and token counts, return the cost in USD 
    for that provider/model, using your updated JSON structure. If we don't
    find the provider or model, return 0.0 by default.
    """
    pricing_list = LLM_CONFIG.get("pricing", [])

    # 1. Find the correct provider block
    provider_block = None
    for p in pricing_list:
        if p["provider"] == provider:
            provider_block = p
            break
    
    # If provider not found, cost = 0
    if not provider_block:
        return 0.0

    # 2. Find the model in the provider’s models
    chosen_model = None
    for m in provider_block.get("models", []):
        if m["name"] in model_name:
            chosen_model = m
            break
    
    # If model not found, cost = 0
    if not chosen_model:
        return 0.0

    # 3. Extract prices per million tokens & calculate cost
    input_price_per_million = chosen_model.get("input", 0.0)
    output_price_per_million = chosen_model.get("output", 0.0)

    input_cost = (input_tokens / 1_000_000) * input_price_per_million
    output_cost = (output_tokens / 1_000_000) * output_price_per_million

    total_cost = input_cost + output_cost
    return round(total_cost, 8)


def detect_tool_use(messages: List[Message]) -> bool:
    for msg in messages:
        if msg.tool_calls is not None:
            return True
    return False


def parse_timestamp(ts: Union[int, str]) -> datetime:
    if isinstance(ts, int):
        return datetime.fromtimestamp(ts)
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))
