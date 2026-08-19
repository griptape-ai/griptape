import os
import uuid

from griptape.drivers.memory.conversation.dakera import DakeraConversationMemoryDriver
from griptape.memory.structure import ConversationMemory
from griptape.structures import Agent

conversation_id = uuid.uuid4().hex
dakera_conversation_driver = DakeraConversationMemoryDriver(
    base_url=os.environ["DAKERA_BASE_URL"],
    api_key=os.environ["DAKERA_API_KEY"],
    conversation_id=conversation_id,
)

agent = Agent(conversation_memory=ConversationMemory(conversation_memory_driver=dakera_conversation_driver))

agent.run("My name is Jeff.")
agent.run("What is my name?")
