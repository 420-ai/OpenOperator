from typing import List, Dict, Any, Optional, Tuple
from core.models import Message, TextContent, ImageContent
import json

def convert_messages_to_openai(messages: List[Message]) -> List[Dict[str, Any]]:
    result = []

    for msg in messages:
        msg_dict = {"role": msg.role}

        # Assistant calling a tool
        if msg.role == "assistant" and msg.tool_calls:
            msg_dict["content"] = None
            msg_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.arguments) if isinstance(tc.arguments, dict) else tc.arguments
                    }
                }
                for tc in msg.tool_calls
            ]

        # Tool responding to the assistant
        elif msg.role == "tool" and msg.tool_result:
            msg_dict.update({
                "tool_call_id": msg.tool_result.call_id,
                "name": msg.tool_result.name,
                "content": json.dumps(msg.tool_result.content) if isinstance(msg.tool_result.content, dict) else msg.tool_result.content
            })

        # Regular multimodal or text message
        else:
            if isinstance(msg.content, list):
                content = []
                for c in msg.content:
                    if isinstance(c, TextContent):
                        content.append({"type": "text", "text": c.text})
                    elif isinstance(c, ImageContent):
                        content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": c.url or f"data:{c.media_type};base64,{c.data}"
                            }
                        })
                msg_dict["content"] = content
            else:
                msg_dict["content"] = msg.content

        result.append(msg_dict)

    return result


def convert_messages_to_anthropic(messages: List[Message]) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    system = None
    converted = []

    for msg in messages:
        if msg.role == "system":
            if system is None:
                system = msg.content if isinstance(msg.content, str) else " ".join(
                    c.text for c in msg.content if isinstance(c, TextContent)
                )
            continue

        content = []

        # Handle multimodal content
        if msg.content and isinstance(msg.content, list):
            for c in msg.content:
                if isinstance(c, TextContent):
                    content.append({"type": "text", "text": c.text})
                elif isinstance(c, ImageContent):
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": c.media_type,
                            "data": c.data
                        }
                    })

        # Tool call message
        if msg.tool_calls:
            for call in msg.tool_calls:
                content.append({
                    "type": "tool_use",
                    "id": call.id,
                    "name": call.name,
                    "input": call.arguments if isinstance(call.arguments, dict) else json.loads(call.arguments)
                })

        # Tool response message
        if msg.tool_result:
            content.append({
                "type": "tool_result",
                "tool_use_id": msg.tool_result.call_id,
                "content": json.dumps(msg.tool_result.content) if isinstance(msg.tool_result.content, dict) else msg.tool_result.content
            })

        if not content and isinstance(msg.content, str):
            content.append({"type": "text", "text": msg.content})

        # FIX: change role from 'tool' → 'user' for tool_result
        role = "user" if msg.role == "tool" and msg.tool_result else msg.role

        converted.append({
            "role": role,
            "content": content
        })

    return system, converted


def convert_messages_to_ollama(messages: List[Message]) -> List[Dict[str, Any]]:
    result = []

    for msg in messages:
        msg_dict: Dict[str, Any] = {"role": msg.role}

        # Tool response message
        if msg.role == "tool" and msg.tool_result:
            msg_dict["name"] = msg.tool_result.name
            msg_dict["content"] = (
                json.dumps(msg.tool_result.content)
                if isinstance(msg.tool_result.content, dict)
                else msg.tool_result.content
            )

        # Assistant tool call message
        elif msg.role == "assistant" and msg.tool_calls:
            msg_dict["content"] = ""  # Ollama requires content even with tool_calls
            msg_dict["tool_calls"] = [
                {
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": tc.arguments if isinstance(tc.arguments, dict) else json.loads(tc.arguments)
                    }
                }
                for tc in msg.tool_calls
            ]

        # Normal or multimodal message
        else:
            content_str = ""
            images = []

            if isinstance(msg.content, list):
                for item in msg.content:
                    if isinstance(item, TextContent):
                        content_str += item.text + "\n"
                    elif isinstance(item, ImageContent):
                        images.append(item.data)
            elif isinstance(msg.content, str):
                content_str = msg.content

            msg_dict["content"] = content_str.strip()

            if images:
                msg_dict["images"] = images

        result.append(msg_dict)

    return result
