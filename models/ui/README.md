# UI Model

This model recognizes UI elements on the screenshot. Source: https://github.com/microsoft/OmniParser

## Install

Run `uv sync`

## Weights

Ensure you have the V2 weights downloaded in weights folder (**ensure caption weights folder is called icon_caption_florence**). If not download them with:

```
rm -rf weights/icon_detect weights/icon_caption weights/icon_caption_florence
for folder in icon_caption icon_detect; do uv run huggingface-cli download microsoft/OmniParser-v2.0 --local-dir weights --repo-type model --include "$folder/*"; done
mv weights/icon_caption weights/icon_caption_florence
```

## Test

Test it via command `uv run gradio_demo.py`.

Open `http://localhost:7861` and test it by uploading some screenshot.

Kill it.

# Run

Run the server via `uv run server/omniparserserver.py`.
