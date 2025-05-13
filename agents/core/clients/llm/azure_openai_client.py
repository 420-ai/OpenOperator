import os
from typing import List
from core.clients.llm.converters import convert_messages_to_openai
from core.clients.llm.parsers import parse_openai_response
from core.clients.llm.utils import detect_tool_use
from core.models import LLMResponse, Message
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
load_dotenv()

class OOAzureOpenAIClient:
    def __init__(self, deployment: str, model: str):

        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )

        self.client = AzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_BASEURL"),
            azure_ad_token_provider=token_provider,
        )
        self.model = model
        self.deployment = deployment

    def call(self, messages: List[Message], tools=None, tool_choice="auto", n=1, temperature=0.1) -> LLMResponse:
        provider_msgs = convert_messages_to_openai(messages)

        params = {
            "model": self.deployment,
            "messages": provider_msgs,
            "n": n,
            "temperature": temperature,
        }

        if tools or detect_tool_use(messages):
            params["tools"] = tools
            params["tool_choice"] = tool_choice

        response = self.client.chat.completions.create(**params)
        return parse_openai_response(response, "azure")