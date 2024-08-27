import os
import uuid

from griptape.drivers import RedisConversationMemoryDriver
from griptape.memory.structure import ConversationMemory
from griptape.structures import Agent

conversation_id = uuid.uuid4().hex
redis_conversation_driver = RedisConversationMemoryDriver(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    password=os.environ["REDIS_PASSWORD"],
    index=os.environ["REDIS_INDEX"],
    conversation_id=conversation_id,
)

agent = Agent(conversation_memory=ConversationMemory(conversation_memory_driver=redis_conversation_driver))

agent.run("My name is Jeff.")
agent.run("What is my name?")
