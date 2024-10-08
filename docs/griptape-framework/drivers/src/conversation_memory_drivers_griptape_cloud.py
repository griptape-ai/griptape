import os

from griptape.drivers import GriptapeCloudConversationMemoryDriver
from griptape.memory.structure import ConversationMemory
from griptape.structures import Agent

cloud_conversation_driver = GriptapeCloudConversationMemoryDriver(
    api_key=os.environ["GT_CLOUD_API_KEY"],
    alias="my_thread_alias",
)
agent = Agent(conversation_memory=ConversationMemory(conversation_memory_driver=cloud_conversation_driver))

agent.run("My name is Jeff.")
agent.run("What is my name?")
