import gradio as gr

with gr.Blocks() as app:
    gr.Markdown("# test ui")

if __name__ == "__main__":
    app.launch()