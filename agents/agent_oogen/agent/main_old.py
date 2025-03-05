from autogen_agentchat.agents import AssistantAgent
from agent.tools.get_weather import get_weather
from agent.tools.get_stock_price import get_stock_price
from agent.llm_clients.azure_openai import llm_client

agent = AssistantAgent(
        name="my_assistant", 
        model_client=llm_client, 
        system_message="You are a helpful AI assistant.",
        tools=[get_weather, get_stock_price]
    )