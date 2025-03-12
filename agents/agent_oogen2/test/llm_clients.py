import asyncio
import os
from autogen_core.models import UserMessage
from agent.clients.llm.azure_openai import llm_gpt4o
from PIL import Image
from autogen_core import Image as AutogenImage

async def test_azure():
    response = await llm_gpt4o.create(
        messages=[
            UserMessage(content="Tell me a joke", source="xxx"),
        ]
    )
    print(response.content)

if __name__ == "__main__":
    print("-" * 20)
    print("Testing Azure GPT-4o ...")
    asyncio.run(test_azure())

    print("-" * 20)
    print("Testing completed.")