from core.clients.llm.anthropic_client import OOAnthropicClient
from core.test.llm_clients.test_messages import test_messages
from dotenv import load_dotenv
load_dotenv()

tools = [
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

    client = OOAnthropicClient(
        model="claude-3-7-sonnet-20250219"
    )

    test_messages(
        "anthropic",
        clientText=client,
        clientMultimodal=client,
        clientTools=client,
        tools=tools
    )
