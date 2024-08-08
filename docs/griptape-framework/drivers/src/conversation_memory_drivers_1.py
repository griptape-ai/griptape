from griptape.drivers import LocalConversationMemoryDriver
from griptape.memory.structure import ConversationMemory
from griptape.structures import Agent

local_driver = LocalConversationMemoryDriver(file_path="memory.json")
agent = Agent(conversation_memory=ConversationMemory(driver=local_driver))

agent.run("Surfing is my favorite sport.")
agent.run("What is my favorite sport?")
