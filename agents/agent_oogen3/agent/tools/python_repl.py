from typing import Annotated
from autogen_ext.tools.langchain import LangChainToolAdapter
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool

langchain_repl_tool = PythonREPL()

@tool
def python_repl(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        result = langchain_repl_tool.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    return (
        result_str + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."
    )

python_repl_tool = LangChainToolAdapter(python_repl)