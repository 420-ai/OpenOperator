import os
from typing import List
from core.clients.llm.converters import convert_messages_to_ollama
from core.clients.llm.parsers import parse_ollama_response
from core.clients.llm.utils import detect_tool_use
from core.models import LLMResponse, Message
from ollama import Client

class OOOllamaClient:
    def __init__(self, model: str):
        self.client = Client(host=os.getenv("OLLAMA_URL", "http://127.0.0.1:11434"))
        self.model = model

    def call(self, messages: List[Message], tools=None) -> LLMResponse:
        provider_msgs = convert_messages_to_ollama(messages)

        response = self.client.chat(
            model=self.model,
            messages=provider_msgs,
            tools=tools if tools or detect_tool_use(messages) else None
        )
        return parse_ollama_response(response)