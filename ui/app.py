import gradio as gr

import asyncio
from pathlib import Path

from agent import create_chat_client
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult

from novnc_proxy import start_websockify

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

load_dotenv()
agent = create_chat_client()


async def handle_message(message, history):
    # This function will be called when the user sends a message, it should be fed into agent
    # with results returned to the user
    response_content = ""
    history.append(message)

    async for response in agent.run_stream(
        task=TextMessage(source="User", content=message)
    ):
        if isinstance(response, TaskResult):
            response_content = response.messages[-1].content
        elif response.type == "ToolCallExecutionEvent":
            response_content = "Calling a tool...\n"
        elif response.type == "ToolCallSummaryMessage":
            response_content += response.content
        elif response.type == "ModelClientStreamingChunkEvent":
            response_content += response.content

        if len(response_content) > 0:
            yield response_content


# create a FastAPI app
app = FastAPI()

# create a static directory to store the static files
static_dir = Path("./static")
static_dir.mkdir(parents=True, exist_ok=True)

# mount FastAPI StaticFiles server
app.mount("/static", StaticFiles(directory=static_dir), name="static")

with gr.Blocks(theme=gr.themes.Ocean()) as demo:
    gr.Markdown("# Echo Operator")
    with gr.Row():
        with gr.Column(scale=5):
            gr.Markdown("## Operator Chat")
            gr.ChatInterface(
                handle_message,
                chatbot=gr.Chatbot(label="Echo Operator", type="messages"),
                type="messages",
            )
        with gr.Column(min_width=1280):
            gr.Markdown("## Agent Screen")
            # an iframe to display a VNC screen
            gr.HTML(
                """
                <iframe src="/static/novnc/vnc.html" width="1280" height="800" frameborder="0"></iframe>
                """,
                padding=False,
                min_height=1000,
            )

# mount Gradio app to FastAPI app
app = gr.mount_gradio_app(app, demo, path="/")


if __name__ == "__main__":
    import subprocess
    import signal
    import os

    process = subprocess.Popen(
        ["uv", "run", "novnc_proxy.py", f"--target-host={os.getenv("VNC_TARGET_HOST")}", "--target-port=5900"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        start_new_session=True,
        creationflags=subprocess.DETACHED_PROCESS
    )

    ## listen for SIGTERM, kill the detached process if received
    def signal_handler(sig, frame):
        print("SIGTERM received, killing the detached process...")
        os.kill(process.pid, signal.SIGTERM)
        
    signal.signal(signal.SIGTERM, signal_handler)

    uvicorn.run(
        "app:app", host="127.0.0.1", port=7860, reload=True, timeout_graceful_shutdown=0
    )
