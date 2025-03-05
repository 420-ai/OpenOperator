import os
import sys
import asyncio

from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from playwright.async_api import async_playwright

from dotenv import load_dotenv

import textwrap

import logging

from autogen_agentchat import TRACE_LOGGER_NAME

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

    async with async_playwright() as pw:
        browser = await pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pw_context = browser.contexts[0]

        # Define an agent
        web_surfer_agent = MultimodalWebSurfer(
            name="WebSurferAgent",
            model_client=model_client,
            # headless=False,
            playwright=pw,
            context=pw_context,
            description="""
                An expert web surfer agent that can navigate the web and perform tasks on behalf of the user. It can do pretty all
                the tasks that a human can do on the web, except filling in the forms for logging in.
            """,
        )

        user_proxy_agent = UserProxyAgent(
            name="UserProxyAgent",
            description="""
            An agent that acts as a proxy for the user. This is used when 'User intervention needed' is detected. 
            User interventions are needed ONLY for the following cases:
            - The agent needs to log in to a website
            - The agent needs to fill in forms that require personal information
            """,
        )

        termination_agent = AssistantAgent(
            name="NextStepAgent",
            description="An agent that determines whether the task is accomplished or if user intervention is needed.",
            model_client=model_client,
            system_message="""
                You are an agent who can determine whether the task has been accomplished by the Web agent.
                
                - If the task goal is accomplished, you should respond with "Termination: task completed".
                - If the task goal is not accomplished yet and if you think the WebSurferAgent can achieve the next step towards completing the task, you will respond with "WebSurferAgent: continue with next step". 
                - If the next task step requires user intervention, you should respond with "User intervention needed. The agent needs your help because <reason>. You need to perform <action> for me".
                    substitute <reason> and <action> with the appropriate values.          
            """,
        )

        # Define a team
        termination = MaxMessageTermination(25) | TextMentionTermination(
            "Termination: task completed"
        )

        agent_team = SelectorGroupChat(
            [web_surfer_agent, termination_agent, user_proxy_agent],
            model_client=model_client,
            selector_prompt="""You are in a role play game. The following roles are available:
    {roles}. Read the following conversation. Then select the next role from {participants} to play. Only return the role.

    {history}

    Read the above conversation. Then select the next role from {participants} to play. Only return the role.
    """,
            termination_condition=termination,
        )

        # # Run the team and stream messages to the console
        stream = agent_team.run_stream(
            task=textwrap.dedent("""
                                            Perform the following task:
                                            - Navigate to https://github.com
                                            - go to the `420-ai/OpenOperator` repository
                                            - Login if necessary
                                            - Find the latest pull requests
                                            - Read the descriptions of those pull requests
                                            - Summarize the pull requests and their descriptions in the markdown format, prioritize these according importance that you think I should pay attention to
                                        """)
        )
        await Console(stream)
        # Close the browser controlled by the agent
        await web_surfer_agent.close()


asyncio.run(main())
