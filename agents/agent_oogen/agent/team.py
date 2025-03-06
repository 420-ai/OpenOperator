from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMessageTermination

from agent.agent_me import OOMeAgent

agent_me = OOMeAgent()

termination_condition = TextMessageTermination(agent_me.name)

team = RoundRobinGroupChat(
        [agent_me],
        termination_condition=termination_condition,
    )