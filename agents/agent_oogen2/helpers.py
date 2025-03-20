import base64
import random
import string
from datetime import datetime
import os
from typing import Any, List
from PIL import Image
import os
import json
import io
import copy

# AUTOGEN related
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import AgentEvent, ChatMessage, HandoffMessage, MemoryQueryEvent, UserInputRequestedEvent, TextMessage, MultiModalMessage, ToolCallRequestEvent, ToolCallExecutionEvent, ToolCallSummaryMessage, ThoughtEvent, ModelClientStreamingChunkEvent, StopMessage
from autogen_core.models import UserMessage, SystemMessage, AssistantMessage, FunctionExecutionResultMessage, CreateResult
from autogen_agentchat.base._chat_agent import Response as ChatAgentResponse

def random_string(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def save_image(image: Image.Image, file_path: str,  file_name: str):
    image_file = os.path.join(file_path, file_name)
    image.save(image_file, format="PNG", optimize=True)

def save_txt(content: str, file_path: str, file_name: str):
    txt_file = os.path.join(file_path, file_name)
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(content)

def save_json(content: dict, file_path: str, file_name: str):
    json_file = os.path.join(file_path, file_name)
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)


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



# Custom related
def format_messages(messages: list[dict]):
    messages_copy = copy.deepcopy(messages)  # Create a deep copy to avoid modifying the original list
    
    for message in messages_copy:
        if "content" in message and isinstance(message["content"], list):
            for content_item in message["content"]:
                if content_item.get("type") == "image_url" and "image_url" in content_item:
                    content_item["image_url"]["url"] = "<BASE64_IMAGE>"
    
    return messages_copy

# AUTOGEN related
def format_autogen_message(message: AgentEvent | ChatMessage | TaskResult) -> str:
    msg_str = ""

    if type(message) == TaskResult:
        msg_str = format_task_result(message)
    elif type(message) == CreateResult:
        msg_str = format_create_result(message)
    elif type(message) in [TextMessage, MultiModalMessage, StopMessage, ToolCallSummaryMessage, HandoffMessage]:
        msg_str = format_message(message)
    elif type(message) in [ToolCallRequestEvent, ToolCallExecutionEvent, MemoryQueryEvent, 
                            UserInputRequestedEvent, ModelClientStreamingChunkEvent, ThoughtEvent]:
        msg_str = format_message(message)
    elif type(message) in [SystemMessage, UserMessage, AssistantMessage, FunctionExecutionResultMessage]:
        msg_str = format_message(message)
    elif type(message) == ChatAgentResponse:
        msg_str = format_response(message)
    else:
        raise ValueError(f"Unsupported message type: {type(message)}")

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

def format_create_result(obj: CreateResult) -> str:
    """Formats the CreateResult into a structured string."""
    formatted_messages = []
    formatted_messages.append(f"====== CreateResult ======")

    if obj.usage:
        formatted_messages.append(f"Usage: {obj.usage}")

    if obj.thought:
        formatted_messages.append(f"Thought: {obj.thought}")

    formatted_messages.append(f"Content:\n {obj.content}")
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

    elif isinstance(msg, SystemMessage):  
        formatted_message.append(f"System Message: {msg.content.strip()}")

    elif isinstance(msg, UserMessage):  
        content_list = [str(content) if not isinstance(content, Image.Image) else "<Image>" for content in msg.content]
        formatted_message.append(f"User Message:\n" + "\n".join(content_list))

    elif isinstance(msg, AssistantMessage): 
        formatted_message.append(f"Assistant Message: {msg.content.strip()}")

    elif isinstance(msg, FunctionExecutionResultMessage):  
        for result in msg.content:
            formatted_message.append(
                f"Function ({result.name}, ID: {result.call_id}): {'Error: ' if result.is_error else 'Result: '}{result.content}"
            )

    formatted_message.append(f"------------------------")

    return "\n".join(formatted_message)

def format_response(response: ChatAgentResponse) -> str:
    """Formats the response into a structured string."""
    formatted_response = []
    formatted_response.append(f"====== Response ======")

    if response.chat_message:
        formatted_response.append(f"Chat Message: {response.chat_message.content.strip()}")

    if response.inner_messages:
        formatted_response.append(f"Inner Messages:")
        for msg in response.inner_messages:
            formatted_response.append(format_autogen_message(msg))

    formatted_response.append(f"========================")

    return "\n".join(formatted_response)