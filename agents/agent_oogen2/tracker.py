from pathlib import Path
from typing import Any, List, Tuple, Union
from helpers import format_autogen_message, get_timestamp, save_txt, save_json, save_image
from PIL import Image
from datetime import datetime
import json
import os
from workflow.clients.computer import ComputerClient

# AUTOGEN related
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import HandoffMessage, MemoryQueryEvent, UserInputRequestedEvent, TextMessage, MultiModalMessage, ToolCallRequestEvent, ToolCallExecutionEvent, ToolCallSummaryMessage, ThoughtEvent, ModelClientStreamingChunkEvent, StopMessage
from autogen_core.models import UserMessage, SystemMessage, AssistantMessage, FunctionExecutionResultMessage, CreateResult
from autogen_agentchat.base._chat_agent import Response as ChatAgentResponse

class Tracker:
    def __init__(self, timestamp: str):
        CURRENT_FOLDER = Path(__file__).resolve().parent
        RUN_DIR = CURRENT_FOLDER / "tracker" / timestamp
        RUN_DIR.mkdir(parents=True, exist_ok=True)
        
        self.run_dir = RUN_DIR
        # self.computer = computer

    # def start_recording(self):
    #     # Start recording
    #     self.computer.start_recording()

    # def end_recording(self):
    #     # Stop recording and save the file
    #     self.computer.end_recording()
    #     self.computer.get_recording(os.path.join(self.run_dir, "recording.mp4"))

    def save(self, name: str, objects: Union[Any, List[Tuple[str, Any]]]) -> str:
        """Save objects (text, images, JSON) into a timestamped folder with specified names."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S.%f")[:-3]
        folder_name = f"{timestamp}_{name}"
        save_path = self.run_dir / folder_name
        save_path.mkdir(parents=True, exist_ok=True)

        if not isinstance(objects, list):
            raise ValueError("Objects must be a list of (filename, object) tuples.")

        for filename, obj in objects:
            file_path = save_path / filename
            
            if isinstance(obj, str):  # Text
                file_path = file_path.with_suffix(".txt")
                file_path.write_text(obj, encoding='utf-8')
            elif isinstance(obj, dict) or isinstance(obj, list):  # JSON or List
                file_path = file_path.with_suffix(".json")
                file_path.write_text(json.dumps(obj, indent=4), encoding='utf-8')
            elif isinstance(obj, Image.Image):  # Image
                file_path = file_path.with_suffix(".png")
                obj.save(file_path)
            elif type(obj) in [TaskResult, 
                               CreateResult, 
                               TextMessage, 
                               MultiModalMessage, 
                               StopMessage, 
                               ToolCallSummaryMessage, 
                               HandoffMessage, 
                               ToolCallRequestEvent, 
                               ToolCallExecutionEvent, 
                               MemoryQueryEvent, 
                               UserInputRequestedEvent, 
                               ModelClientStreamingChunkEvent, 
                               ThoughtEvent, 
                               SystemMessage, 
                               UserMessage, 
                               AssistantMessage, 
                               FunctionExecutionResultMessage, 
                               ChatAgentResponse]:
                file_path = file_path.with_suffix(".txt")
                text = format_autogen_message(obj)
                file_path.write_text(text, encoding='utf-8')
            else:
                print(f"Unsupported object type: {type(obj)}. Skipping...")
        
        return str(save_path)
