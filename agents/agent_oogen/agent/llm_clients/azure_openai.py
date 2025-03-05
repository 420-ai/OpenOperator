from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv()  

# AZURE ---------
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_OPENAI_BASEURL = os.getenv("AZURE_OPENAI_BASEURL")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# LLM
llm_client = AzureOpenAIChatCompletionClient(
    model=AZURE_OPENAI_DEPLOYMENT,
    azure_endpoint=AZURE_OPENAI_BASEURL,
    api_version=AZURE_OPENAI_API_VERSION,
    api_key=AZURE_API_KEY, 
)