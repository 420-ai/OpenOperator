import asyncio
import os
from autogen_core.models import UserMessage
from workflow.clients.llm import llm_gpt4o, llm_gpt4o_mini, llm_o3_mini
from workflow.clients.llm import llm_phi4, llm_llama32_vision
from PIL import Image
from autogen_core import Image as AutogenImage

async def test_azure_gpt4o():
    response = await llm_gpt4o.create(
        messages=[
            UserMessage(content="Tell me a joke", source="xxx"),
        ]
    )
    print(response.content)

async def test_azure_gpt4o_mini():
    response = await llm_gpt4o_mini.create(
        messages=[
            UserMessage(content="Tell me a joke", source="xxx"),
        ]
    )
    print(response.content)

async def test_azure_o3_mini():
    response = await llm_o3_mini.create(
        messages=[
            UserMessage(content="Tell me a joke", source="xxx"),
        ]
    )
    print(response.content)

async def test_ollama_phi4():
    response = await llm_phi4.create(
        messages=[
            UserMessage(content="Tell me a joke", source="xxx"),
        ]
    )
    print(response.content)

async def test_ollama_llama32vision():
    current_dir = os.path.dirname(__file__)
    img = Image.open(os.path.join(current_dir, 'img/test_picture.jpg'))

    response = await llm_llama32_vision.create(
        messages=[
            UserMessage(content=[
                "What is on the picure?",
                AutogenImage.from_pil(img)
            ], source="xxx"),
        ]
    )
    print(response.content)

if __name__ == "__main__":
    print("-" * 20)
    print("Testing Azure o3 mini ...")
    asyncio.run(test_azure_o3_mini())

    print("-" * 20)
    print("Testing Azure GPT-4o ...")
    asyncio.run(test_azure_gpt4o())

    print("-" * 20)
    print("Testing Azure GPT-4o mini ...")
    asyncio.run(test_azure_gpt4o_mini())

    print("-" * 20)
    print("Testing Ollama Phi-4 ...")
    asyncio.run(test_ollama_phi4())

    print("-" * 20)
    print("Testing Ollama Llama-32-Vision ...")
    asyncio.run(test_ollama_llama32vision())

    print("-" * 20)
    print("Testing completed.")