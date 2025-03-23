# LLM Clients

This module abstracts away the differences between various LLM provider APIs, offering a single, consistent interface to send prompts, handle responses, and support advanced features like _tool usage_ and _multimodal messages_. Whether you're using **OpenAI**, **Anthropic**, or **Ollama**, the **experience remains the same**.

## Universal client

> The `LLMClient` provides unified way to call any LLM vendor.

### 🔗 OpenAI example

```python
client_openai = LLMClient(
    provider="openai",
    model="gpt-4o-mini"
)
```

### ☁️ Azure OpenAI example

```python
client_azureopenai = LLMClient(
    provider="azure",
    model="gpt-4o-mini",
    deployment="gpt-4o-mini-deployment",
)
```

### 🦙 Ollama example

```python
client_ollama = LLMClient(
    provider="ollama",
    model="mistral:latest",
)
```

### 🤖 Anthropic example

```python
client_anthropic = LLMClient(
    provider="anthropic",
    model="claude-3-7-sonnet-20250219"
)
```

---

## Messages

We also aligned the formats for **all types of Messages** => no more struggles with finding the correct message format for each vendor

### ✅ 1) Normal Text Message

```python
Message(
    role="user",
    content="Hello, how are you?"
)
```

Or with `TextContent` block (for consistency with multimodal):

```python
Message(
    role="user",
    content=[
        TextContent(type="text", text="Hello, how are you?")
    ]
)
```

---

### ✅ 2) Multimodal Message (Text + Image)

```python
Message(
    role="user",
    content=[
        TextContent(type="text", text="What is in this image?"),
        ImageContent(
            type="image",
            data=encode_image("screenshot.png"),  # base64 encoded image
            media_type="image/png"
        )
    ]
)
```

✅ This works across **OpenAI**, **Anthropic**, and **Ollama** with our converters.

---

### ✅ 3) Tool Usage Message (Assistant requesting tool)

```python
Message(
    role="assistant",
    content=[
        TextContent(type="text", text="Let me look that up for you.")
    ],
    tool_calls=[
        ToolCall(
            id="tool_call_1",  # must be unique and trackable
            name="get_weather",
            arguments={"location": "Berlin"}
        )
    ]
)
```

### 🛠️ 4) Tool Response

```python
Message(
    role="tool",
    tool_result=ToolResult(
        call_id="tool_call_1",
        name="get_weather",
        content={"temp": "22C", "unit": "celsius"}
    )
)
```

> ✅ This pattern will work for OpenAI, Anthropic, and Ollama with the converter functions we are using.

---

## Responses

All responses are returned as an `LLMResponse` object containing:

- `message`: the unified message returned by the LLM
- `usage`: token usage and cost
- `finish_reason`: reason why the LLM stopped (e.g. `"stop"`, `"length"`)

Example:

```python
response = client_openai.chat([Message(role="user", content="Hi!")])
print(response.message.content)
```
