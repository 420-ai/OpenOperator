from core.clients.llm.openai_client import OOOpenAIClient
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

    client = OOOpenAIClient(
        model="gpt-4o-mini"
    )

    test_messages(
        "openai",
        clientText=client,
        clientMultimodal=client,
        clientTools=client,
        tools=tools
    )
