from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

llm_phi4 = OpenAIChatCompletionClient(
    model="phi4:latest",
    base_url="http://localhost:11434/v1",
    api_key="placeholder",
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": False,
        "family": "unknown",
    },
)

llm_llama32_vision = OpenAIChatCompletionClient(
    model="llama3.2-vision:latest",
    base_url="http://localhost:11434/v1",
    api_key="placeholder",
    model_info={
        "vision": True,
        "function_calling": False,
        "json_output": False,
        "family": "unknown",
    },
)