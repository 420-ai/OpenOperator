from typing import Annotated
from autogen_core.tools import FunctionTool

async def get_weather_fce(city: Annotated[str, "City of interest"]) -> str:
    return f"The weather in {city} is 73 degrees and Sunny."

get_weather = FunctionTool(get_weather_fce, description="Get weather for a given city")