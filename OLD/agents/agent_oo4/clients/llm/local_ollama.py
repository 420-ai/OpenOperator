import os
import json
import uuid
from ollama import Client
from dotenv import load_dotenv
load_dotenv()

class ToolFunction:
    def __init__(self, name: str, arguments: dict):
        self.name = name
        # Ensure it's stored as a JSON string, matching OpenAI behavior
        self.arguments = json.dumps(arguments)

class ToolCall:
    def __init__(self, function: ToolFunction, id: str = None):
        self.id = id or str(uuid.uuid4())
        self.function = function

class LLMResponseOllama:
    def __init__(self, response):
        self._response = response

    @property
    def message(self):
        """Returns the message content."""
        return self._response.message.content
    
    @property
    def message_json(self):
        """Returns the message as a JSON string."""
        return json.dumps({"message": self.message}, indent=2, ensure_ascii=False)

    @property
    def finish_reason(self):
        return self._response.done_reason

    @property
    def usage(self):
        if self._response.prompt_eval_count is not None and self._response.eval_count is not None:
            return {
                "prompt": self._response.prompt_eval_count,
                "completion": self._response.eval_count
            }
        return None
    
    @property
    def tool_calls(self):
        raw_tool_calls = self._response.message.tool_calls
        if not raw_tool_calls:
            return None

        result = []
        for raw_call in raw_tool_calls:
            function = ToolFunction(
                name=raw_call.function.name,
                arguments=raw_call.function.arguments
            )
            tool_call = ToolCall(function=function)
            result.append(tool_call)

        return result
        
    def to_dict(self):
        return {
            "message": self.message,
            "finish_reason": self.finish_reason,
            "usage": self.usage
        }

    def to_json(self, indent: int = 2):
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def __repr__(self):
        return f"<LLMResponseOllama message='{self.message[:30]}...', usage={self.usage}, finish_reason='{self.finish_reason}'>"


class OOOllamaClient:
    def __init__(self, model: str):
        self.client = Client(host=os.getenv("OLLAMA_URL", "http://127.0.0.1:11434"))
        self.model = model

    def call(self, messages, tools=None):
        """
        Creates a chat completion request.

        :param messages: List of messages (system, user, etc.).
        :param tools: Custom tools for the LLM (optional).
        :param tool_choice: Tool selection mode (default: "auto").
        :return: Chat completion result.
        """
        response = self.client.chat(
            model=self.model,
            messages=messages,
            tools=tools
        )
        return LLMResponseOllama(response)


llm_phi4 = OOOllamaClient(
    model="phi4:latest"
)

llm_mistral = OOOllamaClient(
    model="mistral:latest"
)

llm_llama32_vision = OOOllamaClient(
    model="llama3.2-vision:latest"
)

llm_llama33 = OOOllamaClient(
    model="llama3.3:latest"
)