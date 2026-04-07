from griptape.memory.structure import ConversationMemory
from griptape.structures import Agent

agent = Agent(conversation_memory=ConversationMemory())

agent.run("Hello!")

print(agent.conversation_memory)
