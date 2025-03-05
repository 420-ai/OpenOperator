import os
import sys
import asyncio

from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_agentchat.agents import AssistantAgent

from dotenv import load_dotenv

import textwrap

import logging

from autogen_agentchat import EVENT_LOGGER_NAME, TRACE_LOGGER_NAME

logging.basicConfig(level=logging.WARNING)

# For trace logging.
trace_logger = logging.getLogger(TRACE_LOGGER_NAME)
trace_logger.addHandler(logging.StreamHandler())
trace_logger.setLevel(logging.DEBUG)

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def main() -> None:
    model_client = AzureOpenAIChatCompletionClient(
        azure_deployment="gpt-4o",
        model="gpt-4o",
        model_info={
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "family": "gpt-4o",
        },
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        use_ocr=True,
    )

    # Define an agent
    web_surfer_agent = MultimodalWebSurfer(
        name="MultimodalWebSurfer",
        model_client=model_client,
        headless=False,
    )

    termination_agent = AssistantAgent(
        name="DoubleChecker",
        model_client=model_client,
        system_message="You are an agent who can verify the information provided in the most recent message. If the task defined by the Team is completed, respond with 'Task completed'. If the task is not completed, respond with 'Task not completed'.",
    )

    # Define a team
    termination = MaxMessageTermination(15) | TextMentionTermination("Task completed")
    agent_team = RoundRobinGroupChat(
        [web_surfer_agent, termination_agent],
        max_turns=10,
        termination_condition=termination,
    )

    # # Run the team and stream messages to the console
    stream = agent_team.run_stream(
        task=textwrap.dedent("""
                                        Perform the following task:
                                        - Navigate to Reddit for the subreddit r/learnprogramming
                                        - Find the latest post
                                        - Summarize the post
                                    """)
    )
    await Console(stream)
    # Close the browser controlled by the agent
    await web_surfer_agent.close()


asyncio.run(main())
