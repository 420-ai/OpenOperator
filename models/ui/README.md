# UI Model

This model recognizes UI elements on the screenshot. Source: https://github.com/microsoft/OmniParser

## Install

In this folder open terminal

1. Run `conda create -n "ui-model" python==3.12`
2. Run `conda activate ui-model`
3. Run `pip install -r requirements.txt`

## Test

Test it via command `python gradio_demo.py`.

Open `http://localhost:7861` and test it by uploading some screenshot.

Kill it.

# Run

Run the server via `python server/omniparserserver.py`.
