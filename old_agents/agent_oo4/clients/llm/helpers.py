from config import OOConfig

def calculate_cost(usage: dict[str, int], model_name: str, config: OOConfig) -> float:
    config_pricing = config.model_config(model_name)
    prompt_cost_per_1M = config_pricing.prompt
    completion_cost_per_1M = config_pricing.completion
    prompt_cost = (usage["prompt"] / 1000000) * prompt_cost_per_1M
    completion_cost = (usage["completion"] / 1000000) * completion_cost_per_1M

    result_cost = round(prompt_cost + completion_cost, 10) # Rounded to 10 decimal places
    return result_cost