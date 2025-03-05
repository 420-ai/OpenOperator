from typing import Annotated
from autogen_core.tools import FunctionTool

async def get_stock_price_fce(ticker: Annotated[str, "Stock ticker"]) -> str:
    return f"The stock {ticker} price is 409 USD per share."

get_stock_price = FunctionTool(get_stock_price_fce, description="Get stock price for a given ticker")