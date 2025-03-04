import os
import io
import base64
import requests
from typing import List, Union
from PIL import Image

from my_utils import save_to_json
from agent.llm_clients.messages import planning_system_message

class AzureOpenAIClient():
    def __init__(self, deployment_name="gpt-4o", temperature=1.0):

        self.endpoint = os.environ.get("AZURE_ENDPOINT")
        self.api_key = os.getenv("AZURE_API_KEY")
        self.deployment_name = deployment_name
        self.temperature = temperature

        self.headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }
        
        # set the initial system message
        self.system_prompt =  planning_system_message
    
    def plan(self, images, user_query):  
        response = self.process_images(self.system_prompt, user_query, images, max_tokens=4096, temperature=self.temperature, only_text=True)
        return response
    
    def encode_image(self, image: Union[str, Image.Image], format) -> str:
        if isinstance(image, str):
            with open(image, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        elif isinstance(image, Image.Image):
            image = image.convert("RGB")
            buffer = io.BytesIO()
            if format=="JPEG":
                image.save(buffer, format="JPEG")
            elif format=="PNG":
                image.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def get_url_payload(self, url: str) -> dict:
        return {
            "type": "image_url",
            "image_url": {
                "url": url
            }
        }

    def get_base64_payload(self, base64_image: str, format) -> dict:
        if format=="JPEG":
            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                }
            }
        elif format=="PNG":
            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}",
                }
            }

    def process_images(self, system_prompt: str, question: str, images: Union[str, Image.Image, List[Union[str, Image.Image]]], max_tokens=300, temperature=0, only_text=True, format="JPEG") -> str:

        if system_prompt==None:
            system_prompt = "You are a helpful assistant."

        if not isinstance(images, list):
            images = [images]

        content = []

        for image in images:
            if isinstance(image, str) and image.startswith("http"):
                content.append(self.get_url_payload(image))
            else:
                base64_image = self.encode_image(image, format=format)
                content.append(self.get_base64_payload(base64_image, format=format))
        
        content.append({"type": "text", "text": question})

        payload = {
            "messages": [
                {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": system_prompt
                    }
                ]
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
            "frequency_penalty": 0.0,
            "max_tokens": max_tokens,
            "n": 1,
            "presence_penalty": 0.0,
            "temperature": temperature,
            "top_p": 1.0,
        }

        save_to_json(payload, "oai_payload.json")

        # print("Sending request...")
        try:
            response = requests.post(self.endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            raise e

        # return response.json()
        if only_text:
            return response.json()['choices'][0]['message']['content']
        else:
            return response
    

 