from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv()  

# AZURE ---------
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_OPENAI_BASEURL = os.getenv("AZURE_OPENAI_BASEURL")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# LLM
llm_o3_mini = AzureOpenAIChatCompletionClient(
    model="o3-mini",
    azure_deployment="o3-mini-deployment",
    azure_endpoint=AZURE_OPENAI_BASEURL,
    api_version=AZURE_OPENAI_API_VERSION,
    api_key=AZURE_API_KEY, 
)

llm_gpt4o = AzureOpenAIChatCompletionClient(
    model="gpt-4o-2024-11-20",
    azure_deployment="gpt-4o-deployment",
    azure_endpoint=AZURE_OPENAI_BASEURL,
    api_version=AZURE_OPENAI_API_VERSION,
    api_key=AZURE_API_KEY, 
)

llm_gpt4o_mini = AzureOpenAIChatCompletionClient(
    model="gpt-4o-mini",
    azure_deployment="gpt-4o-mini-deployment",
    azure_endpoint=AZURE_OPENAI_BASEURL,
    api_version=AZURE_OPENAI_API_VERSION,
    api_key=AZURE_API_KEY, 
)
