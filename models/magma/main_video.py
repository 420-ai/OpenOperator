from PIL import Image
import torch
from transformers import AutoModelForCausalLM, AutoProcessor
from helpers import extract_frames

# Set device and model parameters
dtype = torch.bfloat16
device = "cuda"
model_id = "microsoft/Magma-8B"

# Load the model and processor
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True, torch_dtype=dtype)
processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
model.to(device)

# Video file path
video_path = "./video/recording.mp4"

# Extract frames from the video
frames = extract_frames(video_path)
if not frames:
    print("No frames extracted. Exiting.")
    exit()

# Resize frames to 256x256 as expected by Magma
frames = [frame.resize((256, 256)) for frame in frames]

# Generate image tokens
image_tokens = "<image_start><image><image_end>\n" * len(frames)

# Create conversation prompt
convs = [
    {"role": "system", "content": "You are an AI that analyzes what is happening in the video."},
    {"role": "user", "content": f"{image_tokens}\nWhat application got opened?"},
    {"role": "assistant", "content": ""}  # Ensuring space for the model's response
]

# Generate the model's prompt using the chat template
prompt = processor.tokenizer.apply_chat_template(convs, tokenize=False, add_generation_prompt=True)

# Prepare input tensors
inputs = processor(images=frames, texts=prompt, return_tensors="pt")
inputs['pixel_values'] = inputs['pixel_values'].unsqueeze(0)  # Ensure correct shape
inputs['image_sizes'] = inputs['image_sizes'].unsqueeze(0)
inputs = inputs.to(device).to(dtype)

# Generation parameters
generation_args = {
    "temperature": 0.3,  # Low temperature for more deterministic output
    "do_sample": True,   # Enable sampling-based generation
    "num_beams": 1,      # Greedy decoding
    "max_new_tokens": 1024,
    "use_cache": True,
}

# Run inference
with torch.inference_mode():
    print("Generating response...")
    output_ids = model.generate(**inputs, **generation_args)
    print("Response generated.")

# Decode output text
response = processor.batch_decode(output_ids, skip_special_tokens=True)[0].strip()

# Print response
print("------------------------------")
print("Response:")
print(response)
