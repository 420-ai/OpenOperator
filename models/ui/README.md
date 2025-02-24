# UI Model

This model recognizes UI elements on the screenshot. Source: https://github.com/microsoft/OmniParser

## Install

In this folder open terminal

1. Run `conda create -n "ui-model" python==3.12`
2. Run `conda activate ui-model`
3. Run `pip install -r requirements.txt`

## Weights

Ensure you have the V2 weights downloaded in weights folder (**ensure caption weights folder is called icon_caption_florence**). If not download them with:

```
rm -rf weights/icon_detect weights/icon_caption weights/icon_caption_florence
for folder in icon_caption icon_detect; do huggingface-cli download microsoft/OmniParser-v2.0 --local-dir weights --repo-type model --include "$folder/*"; done
mv weights/icon_caption weights/icon_caption_florence
```

## Test

Test it via command `python gradio_demo.py`.

Open `http://localhost:7861` and test it by uploading some screenshot.

Kill it.

# Run

Run the server via `python server/omniparserserver.py`.
