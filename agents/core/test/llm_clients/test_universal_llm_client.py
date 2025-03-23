from core.clients.llm.llm_client import LLMClient
from core.test.llm_clients.helpers import encode_image
from core.test.llm_clients.test_messages import test_messages
from dotenv import load_dotenv
load_dotenv()

openai_style_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Use this function to get the current price of a stock.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "The ticker symbol for the stock, e.g. GOOG",
                    }
                },
                "required": ["ticker"],
            },
        }
    },
    {
        "type": "function",
            "function": {
            "name": "get_dividend_date",
            "description": "Use this function to get the next dividend payment date of a stock.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "The ticker symbol for the stock, e.g. GOOG",
                    }
                },
                "required": ["ticker"],
            },
        }
    },
]

anthropic_style_tools = [
    {
        "name": "get_stock_price",
        "description": "Use this function to get the current price of a stock.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The ticker symbol for the stock, e.g. GOOG",
                }
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_dividend_date",
        "description": "Use this function to get the next dividend payment date of a stock.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The ticker symbol for the stock, e.g. GOOG",
                }
            },
            "required": ["ticker"],
        },
    },
]


if __name__ == "__main__":

    # OpenAI
    client_openai = LLMClient(
        provider="openai",
        model="gpt-4o-mini"
    )

    test_messages(
        "openai",
        clientText=client_openai,
        clientMultimodal=client_openai,
        clientTools=client_openai,
        tools=openai_style_tools
    )

    # Azure OpenAI
    client_azureopenai = LLMClient(
        provider="azure",
        model="gpt-4o-mini",
        deployment="gpt-4o-mini-deployment",
    )

    test_messages(
        "azure openai",
        clientText=client_azureopenai,
        clientMultimodal=client_azureopenai,
        clientTools=client_azureopenai,
        tools=openai_style_tools
    )

    # Ollama
    client_ollamaText = LLMClient(
        provider="ollama",
        model="mistral:latest",
    )
    client_ollamaVision = LLMClient(
        provider="ollama",
        model="llama3.2-vision:latest",
    )
    client_ollamaTools = LLMClient(
        provider="ollama",
        model="llama3.2:latest",
    )

    test_messages(
        "ollama",
        clientText=client_ollamaText,
        clientMultimodal=client_ollamaVision,
        clientTools=client_ollamaTools,
        tools=openai_style_tools
    )

    # Anthropic
    client_anthropic = LLMClient(
        provider="anthropic",
        model="claude-3-7-sonnet-20250219"
    )

    test_messages(
        "anthropic",
        clientText=client_anthropic,
        clientMultimodal=client_anthropic,
        clientTools=client_anthropic,
        tools=anthropic_style_tools
    )