import base64
from io import BytesIO
from typing import Any
from PIL import Image
import io
import os
import json

from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import AgentEvent, ChatMessage, HandoffMessage, MemoryQueryEvent, UserInputRequestedEvent, TextMessage, MultiModalMessage, ToolCallRequestEvent, ToolCallExecutionEvent, ToolCallSummaryMessage, ThoughtEvent, ModelClientStreamingChunkEvent, StopMessage

def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def decode_image(base64_str) -> Image:
    return Image.open(BytesIO(base64.b64decode(base64_str)))

def resize_and_compress_image(image: Image.Image, max_size=(1024, 1024)) -> Image.Image:
    """
    Resizes and compresses a PNG image while maintaining quality.

    :param image: PIL Image to be resized and compressed.
    :param max_size: Maximum width and height as a tuple.
    :return: Resized and compressed PIL Image.
    """
    # Resize while keeping the aspect ratio
    image = image.copy()  # Ensure we're not modifying the original image
    image.thumbnail(max_size, Image.LANCZOS)
    
    # Save the image into a BytesIO buffer to re-load it (ensures proper compression)
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG", optimize=True)
    img_bytes.seek(0)

    # Return the compressed image
    return Image.open(img_bytes)

# AUTOGEN related
def format_autogen_message(message: AgentEvent | ChatMessage | TaskResult) -> str:
    msg_str = ""

    if type(message) == TaskResult:
        msg_str = format_task_result(message)
    elif type(message) in [TextMessage, MultiModalMessage, StopMessage, ToolCallSummaryMessage, HandoffMessage]:
        msg_str = format_message(message)
    elif type(message) in [ToolCallRequestEvent, ToolCallExecutionEvent, MemoryQueryEvent, 
                            UserInputRequestedEvent, ModelClientStreamingChunkEvent, ThoughtEvent]:
        msg_str = format_message(message)

    return msg_str

def format_task_result(task_result: TaskResult) -> str:
    """Formats the TaskResult messages into a structured string."""
    formatted_messages = []
    formatted_messages.append(f"====== TaskResult ======")

    for idx, msg in enumerate(task_result.messages, start=1):
        header = f"------ {idx}. {msg.type} - {msg.source} --------" if hasattr(msg, "source") else f"------ {idx}. {msg.type} --------"
        formatted_messages.append(header)

        if isinstance(msg, TextMessage):
            formatted_messages.append(f"{msg.content.strip()}")

        elif isinstance(msg, ToolCallRequestEvent):
            for i, tool_call in enumerate(msg.content, start=1):
                formatted_messages.append(f"{i}. FunctionCall\nname='{tool_call.name}'\narguments='{tool_call.arguments}'")

        elif isinstance(msg, ToolCallExecutionEvent):
            for i, result in enumerate(msg.content, start=1):
                formatted_messages.append(f"{i}. FunctionExecutionResult\nname='{result.name}'\ncontent='{result.content}'")

        elif isinstance(msg, ToolCallSummaryMessage):
            formatted_messages.append(f"content='{msg.content.strip()}'")

        elif isinstance(msg, ThoughtEvent):
            formatted_messages.append(f"Thought: {msg.content.strip()}")

        elif isinstance(msg, ModelClientStreamingChunkEvent):
            formatted_messages.append(f"Streaming Chunk: {msg.content.strip()}")

    formatted_messages.append(f"========================")
    return "\n".join(formatted_messages)

def format_message(msg: Any) -> str:
    """Formats the message into a structured string."""
    formatted_message = []
    formatted_message.append(f"------ {msg.type} - {msg.source} --------" if hasattr(msg, "source") else f"------ {msg.type} --------")

    if isinstance(msg, TextMessage):
        formatted_message.append(f"{msg.content.strip()}")

    elif isinstance(msg, ToolCallRequestEvent):
        for i, tool_call in enumerate(msg.content, start=1):
            formatted_message.append(f"{i}. FunctionCall\nname='{tool_call.name}'\narguments='{tool_call.arguments}'")

    elif isinstance(msg, ToolCallExecutionEvent):
        for i, result in enumerate(msg.content, start=1):
            formatted_message.append(f"{i}. FunctionExecutionResult\nname='{result.name}'\ncontent='{result.content}'")

    elif isinstance(msg, ToolCallSummaryMessage):
        formatted_message.append(f"content='{msg.content.strip()}'")

    elif isinstance(msg, ThoughtEvent):
        formatted_message.append(f"Thought: {msg.content.strip()}")

    elif isinstance(msg, ModelClientStreamingChunkEvent):
        formatted_message.append(f"Streaming Chunk: {msg.content.strip()}")

    formatted_message.append(f"------------------------")

    return "\n".join(formatted_message)

