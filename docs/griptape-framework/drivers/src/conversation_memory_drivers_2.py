import os
import uuid

from griptape.drivers import AmazonDynamoDbConversationMemoryDriver
from griptape.memory.structure import ConversationMemory
from griptape.structures import Agent

conversation_id = uuid.uuid4().hex
dynamodb_driver = AmazonDynamoDbConversationMemoryDriver(
    table_name=os.environ["DYNAMODB_TABLE_NAME"],
    partition_key="id",
    value_attribute_key="memory",
    partition_key_value=conversation_id,
)

agent = Agent(conversation_memory=ConversationMemory(conversation_memory_driver=dynamodb_driver))

agent.run("My name is Jeff.")
agent.run("What is my name?")
