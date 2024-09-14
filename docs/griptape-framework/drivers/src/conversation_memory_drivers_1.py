from griptape.drivers import LocalConversationMemoryDriver
from griptape.memory.structure import ConversationMemory
from griptape.structures import Agent

local_driver = LocalConversationMemoryDriver(persist_file="memory.json")
agent = Agent(conversation_memory=ConversationMemory(conversation_memory_driver=local_driver))

agent.run("Surfing is my favorite sport.")
agent.run("What is my favorite sport?")
