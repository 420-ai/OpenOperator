from core.models import Message, LLMResponse, TextContent, ImageContent, ToolCall, ToolResult
from core.test.llm_clients.helpers import encode_image
from pprint import pprint

def test_messages(provider: str, clientText, clientMultimodal, clientTools, tools):
    print("--------------------------------------")
    print(f"Testing messages ... {provider}")
    print("--------------------------------------")

    # -------------------------------------------
    # Message with string content
    # -------------------------------------------

    txt_msg1 = Message(
        role="user",
        content="Hey, tell me a joke"
    )

    response1 = clientText.call(
        messages=[txt_msg1]
    )

    print("--------------------------------------")
    print("Message with string content")
    print(response1.model_dump_json(indent=2))
    print("--------------------------------------")

    # -------------------------------------------
    # Message with list of content (Only text)
    # -------------------------------------------

    txt_msg2 = Message(
        role="user",
        content=[
            TextContent(type="text", text="Hey, tell me a joke")
        ]
    )


    response2 = clientText.call(
        messages=[txt_msg2]
    )

    print("--------------------------------------")
    print("Message with list of content (Only text)")
    print(response2.model_dump_json(indent=2))
    print("--------------------------------------")

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

    response3 = clientMultimodal.call(
        messages=[multi_msg]
    )

    print("--------------------------------------")
    print("[Multimodal] Message with list of content (text + image)")
    print(response3.model_dump_json(indent=2))
    print("--------------------------------------")

    # -------------------------------------------
    # Message with tools
    # -------------------------------------------

    msg_tools = Message(
        role="user",
        content=[
            TextContent(type="text", text="What is the price of MSFT?")
        ]
    )

    response4 = clientTools.call(
        messages=[msg_tools],
        tools=tools
    )

    print("--------------------------------------")
    print("Message with tools - Testing tool selection")
    print(response4.model_dump_json(indent=2))
    print("--------------------------------------")

    # -------------------------------------------
    # Messages with history of tools
    # -------------------------------------------

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

    response5 = clientTools.call(
        messages=[msg_from_user, resp_from_llm, resp_from_tool],
        tools=tools
    )

    print("--------------------------------------")
    print("Message with tools - Testing tool response processing")
    print(response5.model_dump_json(indent=2))
    print("--------------------------------------")

