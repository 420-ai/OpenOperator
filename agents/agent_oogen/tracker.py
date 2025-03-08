import os
from typing import Any
from config import OOConfig
from helpers import get_timestamp, save_txt, save_json, save_image
from agent.clients.computer.server_client import start_recording, end_recording, get_recording
from PIL import Image
from autogen_core import Image as AutogenImage
from autogen_core.models import UserMessage
from autogen_agentchat.messages import ThoughtEvent, ToolCallRequestEvent, ToolCallExecutionEvent
from autogen_agentchat.base._chat_agent import Response as ChatAgentResponse


class Tracker:
    def __init__(self):
        CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
        RUN_DIR = os.path.join(CURRENT_FOLDER, "logs", get_timestamp())
        os.makedirs(RUN_DIR, exist_ok=True)  

        self.result_dir = RUN_DIR

    def start_recording(self):
        # Start recording
        start_recording()

    def end_recording(self):
        # Stop recording and save the file
        end_recording()
        get_recording(os.path.join(self.result_dir, "recording.mp4"))

    def save_config(self, config: OOConfig):
        save_json(config.value, self.result_dir, "config.json")

    def save_system_message(self, system_message: str):
        save_txt(system_message, self.result_dir, "system_message.txt")

    def set_step(self, step: int):
        self.step_counter = step
        self.step_dir = os.path.join(self.result_dir, f"step_{self.step_counter}")
        os.makedirs(self.step_dir, exist_ok=True)

    def save_origin_screenshot(self, screenshot: Image.Image):
        save_image(screenshot, self.step_dir, "origin.png")

    def save_screenshot_analysis(self, analysis: dict):
        save_image(analysis["parsed_image"], self.step_dir, "parsed_image.png")
        save_json(analysis["parsed_content_list"], self.step_dir, "parsed_elements.json")
    
    def save_resized_screenshot(self, screenshot: Image.Image):
        save_image(screenshot, self.step_dir, "parsed_image_resized.png")
        
    def save_user_message(self, user_message: UserMessage):
        filtered_messages = [msg for msg in user_message.content if not isinstance(msg, AutogenImage)]
        filtered_messages_str = "\n".join([str(msg) for msg in filtered_messages])
        save_txt(filtered_messages_str, self.step_dir, "user_message.txt")
    
    def save_response(self, response: Any, response_counter: int):
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
        else:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("Response type not recognized!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(type(response))

        save_txt(result_str, self.step_dir, f"response_{response_counter}.txt")

        