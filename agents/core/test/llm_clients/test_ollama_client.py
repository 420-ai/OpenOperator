from core.clients.llm.ollama_client import OOOllamaClient
from core.test.llm_clients.test_messages import test_messages
from dotenv import load_dotenv
load_dotenv()

tools = [
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

if __name__ == "__main__":
    
    client_text = OOOllamaClient(
        model="mistral:latest"
    )

    client_multimodal = OOOllamaClient(
        model="llama3.2-vision:latest"
    )

    client_tools = OOOllamaClient(
        model="llama3.2:latest"
    )

    test_messages(
        "ollama",
        clientText=client_text,
        clientMultimodal=client_multimodal,
        clientTools=client_tools,
        tools=tools
    )

