import os
from typing import Any
from config import OOConfig
from helpers import get_timestamp, save_txt, save_json, save_image
from agent.clients.computer.server_client import start_recording, end_recording, get_recording
from PIL import Image
from autogen_core import Image as AutogenImage
from autogen_core.models import UserMessage, SystemMessage, AssistantMessage, FunctionExecutionResultMessage
from autogen_agentchat.messages import TextMessage, ThoughtEvent, ToolCallRequestEvent, ToolCallExecutionEvent
from autogen_agentchat.base._chat_agent import Response as ChatAgentResponse
from autogen_core.model_context import ChatCompletionContext

class Tracker:
    def __init__(self):
        CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
        RUN_DIR = os.path.join(CURRENT_FOLDER, "logs", get_timestamp())
        os.makedirs(RUN_DIR, exist_ok=True)  

        self.result_dir = RUN_DIR
        self.step_counter = 0
        self.current_dir = None

    # Global functions

    def start_recording(self):
        # Start recording
        start_recording()

    def end_recording(self):
        # Stop recording and save the file
        end_recording()
        get_recording(os.path.join(self.result_dir, "recording.mp4"))

    def save_config(self, config: OOConfig):
        save_json(config.value, self.result_dir, "config.json")

    # Entity related functions

    def set_entity_step(self, entity: str):
        """
        entity: str - The entity name (agent, team) to set.
        """
        self.step_counter += 1 
        self.current_dir = os.path.join(self.result_dir, f"step_{self.step_counter}", entity)
        os.makedirs(self.current_dir, exist_ok=True)

    def save_system_message(self, system_message: SystemMessage):
        save_txt(system_message.content, self.current_dir, "system_message.txt")

    def save_origin_screenshot(self, screenshot: Image.Image):
        save_image(screenshot, self.current_dir, "origin.png")

    def save_screenshot_analysis(self, analysis: dict):
        save_image(analysis["parsed_image"], self.current_dir, "parsed_image.png")
        save_json(analysis["parsed_content_list"], self.current_dir, "parsed_elements.json")
    
    def save_resized_screenshot(self, screenshot: Image.Image):
        save_image(screenshot, self.current_dir, "parsed_image_resized.png")
        
    def save_user_message(self, user_message: UserMessage):
        filtered_messages = [msg for msg in user_message.content if not isinstance(msg, AutogenImage)]
        filtered_messages_str = "\n".join([str(msg) for msg in filtered_messages])
        save_txt(filtered_messages_str, self.current_dir, "user_message.txt")
    
    def save_response(self, response: Any, response_counter: int = 1):
        result_str = ""
        if isinstance(response, ThoughtEvent):
            result_str = f"Thought: {response.content}"
        elif isinstance(response, ToolCallRequestEvent):
            for tool_call_resp in response.content:
                tool_call_resp_str = f"Tool Call: {tool_call_resp.name} with args {tool_call_resp.arguments}"
                result_str += tool_call_resp_str + "\n"
        elif isinstance(response, ToolCallExecutionEvent):
            for tool_call_resp in response.content:
                tool_call_resp_str = f"Tool Call Result: {tool_call_resp}"
                result_str += tool_call_resp_str + "\n"
        elif isinstance(response, ChatAgentResponse):
            result_str = f"Response: {response.chat_message.content}"
        elif isinstance(response, TextMessage):
            result_str = f"Text Message: {response.content}"
        else:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("Response type not recognized!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(type(response))

        save_txt(result_str, self.current_dir, f"response_{response_counter}.txt")

    async def save_messages(self, model_context: ChatCompletionContext):
        messages = await model_context.get_messages()

        result_str = ""

        for message in messages:
            if isinstance(message, UserMessage):
                if isinstance(message.content, list):
                    content_list = []
                    for item in message.content:
                        if isinstance(item, AutogenImage):
                            content_list.append("<Image>")
                        else:
                            content_list.append(str(item))
                    content_str = "---\n".join(content_list)
                else:
                    content_str = message.content
                result_str += f"User ({message.source}): {content_str}"
            elif isinstance(message, AssistantMessage):    
                if isinstance(message.content, list):
                    content_str = " | ".join(str(fc) for fc in message.content)
                else:
                    content_str = message.content
                result_str += f"Assistant ({message.source}): {content_str}"
                if message.thought:
                    result_str += f"\nThought: {message.thought}"
            elif isinstance(message, FunctionExecutionResultMessage):
                results_str = "\n".join(
                    f"Function ({result.name}, ID: {result.call_id}): {'Error: ' if result.is_error else 'Result: '}{result.content}"
                    for result in message.content
                )
                result_str += results_str
            else:
                print("Message type not recognized!")

            result_str += "\n-----------------------------------\n"

        save_txt(result_str, self.current_dir, "history_messages.txt")

        