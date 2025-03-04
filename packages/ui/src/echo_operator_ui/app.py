import gradio as gr
from echo_agent_orchestrator.agent import agent
from autogen_agentchat.messages import TextMessage, ChatMessage, AgentEvent
from autogen_agentchat.base import TaskResult


async def handle_message(message, history):
    # This function will be called when the user sends a message, it should be fed into agent
    # with results returned to the user
    response_content = ''
    history.append(message)

    async for response in agent.run_stream(task=TextMessage(source='User', content=message)):
        if isinstance(response, TaskResult):
            response_content = response.messages[-1].content
        elif response.type == 'ToolCallExecutionEvent':
            response_content = 'Calling a tool...\n'
        elif response.type == 'ToolCallSummaryMessage':
            response_content += response.content
        elif response.type == 'ModelClientStreamingChunkEvent':
            response_content += response.content

        if len(response_content) > 0:
            yield response_content

with gr.Blocks(theme=gr.themes.Ocean()) as app:
    gr.Markdown('# Echo Operator')
    with gr.Row():
        with gr.Column(scale=5):
            gr.Markdown('## Operator Chat')
            gr.ChatInterface(
                handle_message,
                chatbot=gr.Chatbot(label='Echo Operator', type='messages'),
                type='messages',
            )
        with gr.Column(scale=7):
            gr.Markdown('## Agent Screen')

if __name__ == '__main__':
    app.launch()
