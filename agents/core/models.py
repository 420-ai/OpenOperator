from typing import List, Optional, Union, Literal, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
# from enum import Enum

# class PROVIDER(Enum):
#     AZURE = "azure"
#     OPENAI = "openai"
#     OLLAMA = "ollama"
#     ANTHROPIC = "anthropic"
#     HUGGINGFACE = "huggingface"


class ImageContent(BaseModel):
    type: Literal["image", "image_url"]
    data: Optional[str] = None
    url: Optional[str] = None
    media_type: Optional[str] = None


class TextContent(BaseModel):
    type: Literal["text"]
    text: str

class ToolCall(BaseModel):
    id: str
    name: str
    arguments: Union[str, Dict[str, Any]]

class ToolResult(BaseModel):
    call_id: str  # maps to id / tool_use_id / tool_call_id
    name: Optional[str] = None
    content: Union[str, Dict[str, Any]]

class Message(BaseModel):
    role: Literal["user", "assistant", "system", "developer", "tool"]
    content: Optional[Union[str, List[Union[TextContent, ImageContent]]]] = None

    tool_calls: Optional[List[ToolCall]] = None  # assistant requesting tools
    tool_result: Optional[ToolResult] = None     # tool response           


class Usage(BaseModel):
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]
    cost: Optional[float] = Field(default=0.0, description="Cost in dollars")


class LLMResponse(BaseModel):
    id: str
    provider: Literal["openai", "azure", "ollama", "anthropic", "huggingface"]
    model: str
    created_at: datetime
    message: Message
    finish_reason: Optional[str]
    usage: Optional[Usage]
