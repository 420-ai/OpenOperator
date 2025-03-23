import os
from typing import List
import anthropic
from core.clients.llm.parsers import parse_anthropic_response
from core.clients.llm.utils import detect_tool_use
from core.models import LLMResponse, Message
from core.clients.llm.converters import convert_messages_to_anthropic


class OOAnthropicClient:
    def __init__(self, model: str):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = model

    def call(
        self,
        messages: List[Message],
        tools=None,
        tool_choice=None,
        max_tokens: int = 1024
    ) -> LLMResponse:
        # Extract system + messages from unified format
        extracted_system, converted_messages = convert_messages_to_anthropic(messages)

        params = {
            "model": self.model,
            "messages": converted_messages,
            "max_tokens": max_tokens,
        }

        # Use explicit `system` if provided, else extracted one
        if extracted_system:
            params["system"] = extracted_system

        # Tool use auto-detection
        if tools or detect_tool_use(messages):
            params["tools"] = tools
            params["tool_choice"] = tool_choice or {"type": "auto"}

        response = self.client.messages.create(**params)
        return parse_anthropic_response(response)
