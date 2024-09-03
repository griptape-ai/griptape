import os
import sys

import boto3

from griptape.drivers import (
    AmazonDynamoDbConversationMemoryDriver,
)
from griptape.memory.structure import ConversationMemory
from griptape.structures import Agent

if len(sys.argv) > 2:
    user_input = sys.argv[1]
    session_id = sys.argv[2]
else:
    user_input = "Hello!"  # Default input
    session_id = "session-id-123"  # Default session ID

structure = Agent(
    conversation_memory=ConversationMemory(
        conversation_memory_driver=AmazonDynamoDbConversationMemoryDriver(
            session=boto3.Session(
                aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            ),
            table_name=os.environ["DYNAMODB_TABLE_NAME"],  # The name of the DynamoDB table
            partition_key="id",  # The name of the partition key
            partition_key_value=session_id,  # The value of the partition key
            value_attribute_key="value",  # The key in the DynamoDB item that stores the memory value
        )
    )
)

print(structure.run(user_input).output_task.output.value)
