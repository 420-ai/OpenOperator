import os
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

## Uncomment below to enable debug logging for autogen
# import logging
# from autogen_core import TRACE_LOGGER_NAME

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(TRACE_LOGGER_NAME)
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)


def create_chat_client():
    """
    Define a model client. You can use other model client that implements
    the `ChatCompletionClient` interface.
    """
    model_client = AzureOpenAIChatCompletionClient(
        model="gpt-4o",
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    )

    # Define a simple function tool that the agent can use.
    # For this example, we use a fake weather tool for demonstration purposes.
    async def get_weather(city: str) -> str:
        """Get the weather for a given city."""
        return f"The weather in {city} is 73 degrees and Sunny."

    # Define an AssistantAgent with the model, tool, system message, and reflection enabled.
    # The system message instructs the agent via natural language.
    return AssistantAgent(
        name="weather_agent",
        model_client=model_client,
        tools=[get_weather],
        system_message="You are a helpful assistant.",
        reflect_on_tool_use=True,
        model_client_stream=True,  # Enable streaming tokens from the model client.
    )
