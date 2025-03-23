from core.models import Message, LLMResponse, TextContent, ImageContent, ToolCall, ToolResult
from core.clients.llm.ollama_client import OOOllamaClient
from core.test.llm_clients.helpers import encode_image


def test_ollama(client_text, client_multimodal, client_tools):
    """
    Test the OOOllamaClient with different message formats.
    """

    # -------------------------------------------
    # Message with string content
    # -------------------------------------------

    txt_msg1 = Message(
        role="user",
        content="Hey, tell me a joke"
    )

    response1 = client_text.call(
        messages=[txt_msg1]
    )

    print("Response 1:", response1)

    # -------------------------------------------
    # Message with list of content (Only text)
    # -------------------------------------------

    txt_msg2 = Message(
        role="user",
        content=[
            TextContent(type="text", text="Hey, tell me a joke")
        ]
    )


    response2 = client_text.call(
        messages=[txt_msg2]
    )

    print("Response 2:", response2)

    # -------------------------------------------
    # Message with list of content (text + image)
    # -------------------------------------------

    multi_msg = Message(
        role="user",
        content=[
            TextContent(type="text", text="What is in this image?"),
            ImageContent(
                type="image",
                data=encode_image("./test_image.png"),  # base64 encoded image
                media_type="image/png"
            )
        ]
    )

    response3 = client_multimodal.call(
        messages=[multi_msg]
    )

    print("Response 3:", response3)

    # -------------------------------------------
    # Message with tools
    # -------------------------------------------

    # tools
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

    msg_tools = Message(
        role="user",
        content=[
            TextContent(type="text", text="What is the current price of MSFT?")
        ]
    )

    response4 = client_tools.call(
        messages=[msg_tools],
        tools=tools
    )

    print("Response 4:", response4)

    # -------------------------------------------
    # Messages with history of tools
    # -------------------------------------------

    # tools
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

    msg_from_user = Message(
        role="user",
        content=[
            TextContent(type="text", text="What is the price of MSFT?")
        ]
    )

    resp_from_llm = Message(
        role="assistant",
        content=[
            TextContent(type="text", text="Let me look that up for you.")
        ],
        tool_calls=[
            ToolCall(
                id="tool_call_1",  # must be unique and trackable
                name="get_stock_price",
                arguments={"ticker": "MSFT"}
            )
        ]
    )

    resp_from_tool = Message(
        role="tool",
        tool_result=ToolResult(
            call_id="tool_call_1",
            # content={"ticker": "MSFT", "current_price": 150.0},
            content="The current price of MSFT is $150.0",
        )
    )

    response5 = client_tools.call(
        messages=[msg_from_user, resp_from_llm, resp_from_tool],
        tools=tools
    )

    print("Response 5:", response5)

