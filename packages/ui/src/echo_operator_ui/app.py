import gradio as gr


def handle_message(message, history):
    # This function will be called when the user sends a message, it should be fed into agent
    # with results returned to the user

    return message


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
