import os
import uuid

from griptape.drivers import GriptapeCloudConversationMemoryDriver
from griptape.memory.structure import ConversationMemory
from griptape.structures import Agent

conversation_id = uuid.uuid4().hex
cloud_conversation_driver = GriptapeCloudConversationMemoryDriver(
    api_key=os.environ["GT_CLOUD_API_KEY"],
)
agent = Agent(conversation_memory=ConversationMemory(conversation_memory_driver=cloud_conversation_driver))

agent.run("My name is Jeff.")
agent.run("What is my name?")
