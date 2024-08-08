from griptape.memory.structure import SummaryConversationMemory
from griptape.structures import Agent

agent = Agent(conversation_memory=SummaryConversationMemory(offset=2))

agent.run("Hello!")

print(agent.conversation_memory.summary)
