# Core

This `Core` package contains shared code across multiple agents. It is the foundation of this project, offering a set of reusable, modular components that ensure consistency, extensibility, and ease of integration across the entire system. It centralizes shared logic, type definitions, and abstract interfaces to minimize vendor lock-in and implementation complexity.

## Models

> Located in `models.py` file.

- **ImageContent**: Represents image-based content, either embedded (`data`) or via URL.
- **TextContent**: Represents text-based content.
- **ToolCall**: Represents a request by the assistant to invoke a tool, including the tool name and input arguments.
- **ToolResult**: Represents the result returned by a tool after execution.
- **Message**: Unified message model supporting roles (`user`, `assistant`, etc.), multi-modal content (text, images), and tool interactions.
- **Usage**: Tracks token usage and optional cost in dollars.
- **LLMResponse**: A complete response from an LLM provider, including message content, usage metrics, and metadata like model name and timestamp.

These models ensure consistent and validated data structures for logging, storing, and processing LLM conversations and tool-augmented workflows.

## LLM clients

> Located in `llm_clients` directory.

The LLM Clients module provides a **unified interface for interacting with different LLM providers** such as OpenAI, Azure OpenAI, Anthropic, and Ollama. It abstracts away the provider-specific differences, enabling seamless message formatting, response handling, tool usage, and multimodal support. Using the LLMClient class, developers can send prompts and receive structured responses in a consistent format across providers, significantly simplifying integration and vendor switching.
More info in [README](./llm_clients/README.md).

## Message store

> Located in `message_store.py` file.

The `MessageStore` is a **lightweight conversation manager** designed to collect, organize, and convert message history across different LLM providers. It supports both raw `Message` objects and structured `LLMResponse` objects, enabling easy tracking of prompts, responses, and token usage over the course of a session.

#### Key Features:

- 🧠 **Conversation History**  
  Maintains a list of user/assistant messages and responses via the `add_message()` method.

- 🔄 **Unified Message Retrieval**  
  Use `get_messages()` to retrieve a clean list of messages, abstracting away internal `LLMResponse` wrappers.

- 🔌 **Provider-Aware Conversion**  
  The `get_messages_dict(provider)` method prepares messages in the appropriate format for OpenAI, Azure OpenAI, Anthropic, and Ollama—handling provider-specific quirks like system prompts automatically.

- 📊 **Token Usage Summary**  
  The `get_usage_stats()` method aggregates token counts (prompt, completion, total) from all recorded LLM responses for easy cost tracking or analysis.

#### Example:

```python
store = MessageStore(conversation_id="my-session")

store.add_message(Message(role="user", content="Hello!"))
response = client.chat(store.get_messages())
store.add_message(response)

formatted = store.get_messages_dict(provider="openai")
usage = store.get_usage_stats()
```

## Test

> Located in `Test` directory.

Module for testing functionality inside the `Core` package.
