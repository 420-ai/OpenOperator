import os
from typing import List
from core.clients.llm.converters import convert_messages_to_openai
from core.clients.llm.parsers import parse_openai_response
from core.clients.llm.utils import detect_tool_use
from core.models import LLMResponse, Message
from openai import AzureOpenAI

class OOAzureOpenAIClient:
    def __init__(self, deployment: str, model: str):
        self.client = AzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_BASEURL"),
            azure_ad_token=os.getenv("AZURE_API_KEY"),
            azure_deployment=deployment,
        )
        self.model = model

    def call(self, messages: List[Message], tools=None, tool_choice="auto", n=1, temperature=0.1) -> LLMResponse:
        provider_msgs = convert_messages_to_openai(messages)

        params = {
            "model": self.model,
            "messages": provider_msgs,
            "n": n,
            "temperature": temperature,
        }

        if tools or detect_tool_use(messages):
            params["tools"] = tools
            params["tool_choice"] = tool_choice

        response = self.client.chat.completions.create(**params)
        return parse_openai_response(response, "azure")