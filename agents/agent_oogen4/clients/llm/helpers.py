from typing import Tuple
from autogen_core.models import RequestUsage
from config import OOConfig

def calculate_cost(usage: RequestUsage, model_name: str, config: OOConfig) -> Tuple[str, float]:
    config_pricing = config.model_config(model_name)
    prompt_cost_per_1M = config_pricing["input"]
    completion_cost_per_1M = config_pricing["output"]
    prompt_cost = (usage.prompt_tokens / 1000000) * prompt_cost_per_1M
    completion_cost = (usage.completion_tokens / 1000000) * completion_cost_per_1M

    result_cost = round(prompt_cost + completion_cost, 10) # Rounded to 10 decimal places
    result_model = config_pricing["name"] # Model name from config
    return result_model, result_cost

def my_calculate_cost(prompt_tokens: int, completion_tokens: int, model_name: str, config: OOConfig) -> Tuple[str, float]:
    config_pricing = config.model_config(model_name)
    prompt_cost_per_1M = config_pricing["input"]
    completion_cost_per_1M = config_pricing["output"]
    prompt_cost = (prompt_tokens / 1000000) * prompt_cost_per_1M
    completion_cost = (completion_tokens / 1000000) * completion_cost_per_1M

    result_cost = round(prompt_cost + completion_cost, 10) # Rounded to 10 decimal places
    result_model = config_pricing["name"] # Model name from config
    return result_model, result_cost