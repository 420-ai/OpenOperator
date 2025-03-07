from PIL import Image
import torch
from transformers import AutoModelForCausalLM
from transformers import AutoProcessor 
from helpers import extract_frames
import os
import cv2

dtype = torch.bfloat16
model = AutoModelForCausalLM.from_pretrained("microsoft/Magma-8B", trust_remote_code=True, torch_dtype=dtype)
processor = AutoProcessor.from_pretrained("microsoft/Magma-8B", trust_remote_code=True)
model.to("cuda")

# Inference
video = "./video/recording.mp4"

frames = extract_frames(video)
print(f"Extracted {len(frames)} frames.")

image_tokens = "\n".join(["<image_start><image><image_end>"] * len(frames))
convs = [
    {"role": "system", "content": "You are an agent that can see, talk, and act."},            
    {"role": "user", "content": f"{image_tokens}\nWhat application got opened?"},
]
prompt = processor.tokenizer.apply_chat_template(convs, tokenize=False, add_generation_prompt=True)
inputs = processor(images=frames, texts=prompt, return_tensors="pt")
inputs['pixel_values'] = inputs['pixel_values'].unsqueeze(0)
inputs['image_sizes'] = inputs['image_sizes'].unsqueeze(0)
inputs = inputs.to("cuda").to(dtype)

generation_args = { 
    "max_new_tokens": 500, 
    "temperature": 0.0, 
    "do_sample": False, 
    "use_cache": True,
    "num_beams": 1,
} 

with torch.inference_mode():
    print("Generating response...")
    generate_ids = model.generate(**inputs, **generation_args)
    print("Response generated.")


print("Decoding response...")
generate_ids = generate_ids[:, inputs["input_ids"].shape[-1] :]
response = processor.decode(generate_ids[0], skip_special_tokens=True).strip()
print("Response decoded.")

print("------------------------------")
print("Response:")
print(response)