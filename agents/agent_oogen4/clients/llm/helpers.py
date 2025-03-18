from autogen_core.models import RequestUsage
from config import OOConfig

def calculate_cost(usage: RequestUsage, model_name: str, config: OOConfig):
    config_pricing = config.model_config(model_name)
    prompt_cost_per_1M = config_pricing["input"]
    completion_cost_per_1M = config_pricing["output"]
    prompt_cost = (usage.prompt_tokens / 1000000) * prompt_cost_per_1M
    completion_cost = (usage.completion_tokens / 1000000) * completion_cost_per_1M
    return round(prompt_cost + completion_cost, 10)  # Rounded to 10 decimal places
