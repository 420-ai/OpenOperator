from pydantic import BaseModel, Field
import copy
import json
from typing import List, Union, Literal, Optional, Dict, Any
from core.models import Message, LLMResponse, Usage, ImageContent
from core.clients.llm.converters import convert_messages_to_openai, convert_messages_to_ollama, convert_messages_to_anthropic

class MessageStore(BaseModel):
    conversation_id: str = "random_id"
    messages: List[Union[Message, LLMResponse]] = Field(default_factory=list)

    def add_message(self, message: Union[Message, LLMResponse]):
        self.messages.append(message)

    def get_messages(self) -> List[Message]:
        """Returns only the message objects from both requests and responses."""
        result = []
        for entry in self.messages:
            if isinstance(entry, Message):
                result.append(entry)
            elif isinstance(entry, LLMResponse):
                result.append(entry.message)
        return result
    
    # def get_messages_dict(self, provider: Literal["openai", "azure", "ollama", "anthropic"]) -> Dict[str, Any]:
    #     """Returns messages and provider-specific params (like system for Anthropic)"""
    #     msgs = self.get_messages()

    #     if provider in {"openai", "azure"}:
    #         return {"messages": convert_messages_to_openai(msgs)}

    #     elif provider == "ollama":
    #         return {"messages": convert_messages_to_ollama(msgs)}

    #     elif provider == "anthropic":
    #         system_prompt, formatted = convert_messages_to_anthropic(msgs)
    #         return {"messages": formatted, "system": system_prompt}

    #     else:
    #         raise ValueError(f"Unknown provider: {provider}")
    
    def get_messages_dict(self, optimized: bool=False) -> Dict[str, Any]:
        msgs = copy.deepcopy(self.get_messages())  # deep copy

        result = []
        if optimized:
            for m in msgs:
                if m.content and isinstance(m.content, list):
                    for c in m.content:
                        if isinstance(c, ImageContent):
                            c.data = "<BASE64_IMAGE>"
                
                result.append(m.model_dump())
        else:
           result = [m.model_dump() for m in msgs]  

        return result 

    def get_usage_stats(self) -> Usage:
        prompt_total = sum(m.usage.prompt_tokens for m in self.messages if isinstance(m, LLMResponse) and m.usage and m.usage.prompt_tokens)
        completion_total = sum(m.usage.completion_tokens for m in self.messages if isinstance(m, LLMResponse) and m.usage and m.usage.completion_tokens)
        return Usage(
            prompt_tokens=prompt_total,
            completion_tokens=completion_total,
            total_tokens=prompt_total + completion_total
        )

