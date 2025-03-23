import logging
from typing import List, Literal, Optional
from core.models import Message, LLMResponse
from core.clients.llm.openai_client import OOOpenAIClient
from core.clients.llm.azure_openai_client import OOAzureOpenAIClient
from core.clients.llm.ollama_client import OOOllamaClient
from core.clients.llm.anthropic_client import OOAnthropicClient

logger = logging.getLogger("core.clients.llm_client")

LLMProvider = Literal["openai", "azure", "anthropic", "ollama"]

class LLMClient:
    """
    UNIVERSAL LLM CLIENT
    ================
    A generic LLM client that can be used to call different LLM providers."
    It abstracts the differences between the providers and provides a unified interface."
    ================
    """
    
    def __init__(
        self,
        provider: LLMProvider,
        model: str,
        deployment: Optional[str] = None,  # Only for Azure
    ):
        self.provider = provider
        self.model = model

        if provider == "openai":
            self.client = OOOpenAIClient(model)
        elif provider == "azure":
            if deployment is None:
                raise ValueError("Azure provider requires 'deployment'")
            self.client = OOAzureOpenAIClient(deployment, model)
        elif provider == "anthropic":
            self.client = OOAnthropicClient(model)
        elif provider == "ollama":
            self.client = OOOllamaClient(model)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def call(
        self,
        messages: List[Message],
        tools=None,
        tool_choice: Optional[str] = "auto",
        temperature: float = 0.1,
        max_tokens: int = 1024,
        n: int = 1,
    ) -> LLMResponse:
        if self.provider in {"openai", "azure"}:
            return self.client.call(
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                n=n,
            )
        elif self.provider == "anthropic":
            return self.client.call(
                messages=messages,
                tools=tools,
                tool_choice={"type": tool_choice} if tool_choice else None,
                max_tokens=max_tokens,
            )
        elif self.provider == "ollama":
            return self.client.call(
                messages=messages,
                tools=tools,
            )
