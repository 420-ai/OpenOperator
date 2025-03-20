import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

class OOAzureOpenAIClient:
    def __init__(self, deployment: str, model: str):
        """
        Initializes the custom LLM client.
        
        :param deployment: The deployment name (e.g., "gpt-4o-deployment").
        """
        self.client = AzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_BASEURL"),
            azure_ad_token=os.getenv("AZURE_API_KEY"),
            azure_deployment=deployment,
        )
        self.model = model 

    def call(self, messages, tools=None, tool_choice="auto"):
        """
        Creates a chat completion request.

        :param messages: List of messages (system, user, etc.).
        :param tools: Custom tools for the LLM (optional).
        :param tool_choice: Tool selection mode (default: "auto").
        :return: Chat completion result.
        """
        return self.client.chat.completions.create(
            model=self.model,  # Deployment name is set during initialization
            messages=messages,
            tools=tools,
            tool_choice=tool_choice
        )

my_llm_gpt4o = OOAzureOpenAIClient(
    deployment="gpt-4o-deployment",
    model="gpt-4o"
)