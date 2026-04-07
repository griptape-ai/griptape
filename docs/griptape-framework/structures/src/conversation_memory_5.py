from griptape.memory.structure import SummaryConversationMemory
from griptape.structures import Agent
from griptape.utils import Conversation

agent = Agent(conversation_memory=SummaryConversationMemory(offset=2))

agent.run("Hello my name is John?")
agent.run("What is my name?")
agent.run("My favorite color is blue.")

print(Conversation(agent.conversation_memory))
