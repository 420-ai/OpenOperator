import mcp.types as types

ALL_TOOLS = [
        types.Tool(
            name="mouse_move",
            description="Moves the mouse cursor to the specified screen coordinates.",
            inputSchema={
                "type": "object",
                "required": ["x", "y"],
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "The x coordinate (absolute) to move to.",
                    },
                    "y": {
                        "type": "integer",
                        "description": "The y coordinate (absolute) to move to.",
                    },
                },
            },
        ),
        types.Tool(
            name="mouse_scroll",
            description="Scrolls the mouse in a specified direction and amount.",
            inputSchema={
                "type": "object",
                "required": ["direction", "amount", "delay", "steps"],
                "properties": {
                    "direction": {
                        "type": "string",
                        "description": "'up', 'down', 'left', 'right'. Determines the direction of scrolling.",
                    },
                    "amount": {
                        "type": "integer",
                        "description": "The scroll amount. Positive values move in the natural direction.",
                    },
                    "delay": {
                        "type": "number",
                        "description": "Delay (in seconds) between consecutive scrolls.",
                    },
                    "steps": {
                        "type": "integer",
                        "description": "Number of times to apply the scroll for smoother motion.",
                    },
                },
            },
        ),
        types.Tool(
            name="mouse_left_click",
            description="Performs a single left mouse click.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="mouse_double_click",
            description="Performs a double left mouse click.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="keyboard_type",
            description="Types a string using the keyboard.",
            inputSchema={
                "type": "object",
                "required": ["text"],
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to type on keyboard.",
                    },
                },
            },
        ),
        types.Tool(
            name="keyboard_hotkeys",
            description="Presses a sequence of hotkeys together (e.g., ['ctrl', 'c']).",
            inputSchema={
                "type": "object",
                "required": ["hotkeys"],
                "properties": {
                    "hotkeys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of hotkeys to press (e.g., ['ctrl', 'v']).",
                    },
                },
            },
        ),
    ]