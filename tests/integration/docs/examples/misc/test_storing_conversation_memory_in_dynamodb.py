import re


class TestStoringConversationMemoryInDynamoDb:
    """
    https://docs.griptape.ai/en/latest/examples/store-conversation-memory-in-dynamodb/
    """

    def test_storing_conversation_memory_in_dynamodb(self):
        import os
        import uuid
        from griptape.drivers import DynamoDbConversationMemoryDriver
        from griptape.memory.structure import ConversationMemory
        from griptape.structures import Agent

        conversation_id = uuid.uuid4().hex
        dynamodb_driver = DynamoDbConversationMemoryDriver(
            table_name=os.getenv("DYNAMODB_TABLE_NAME"),
            partition_key="id",
            value_attribute_key="memory",
            partition_key_value=conversation_id,
        )

        agent = Agent(memory=ConversationMemory(driver=dynamodb_driver))

        agent.run("My name is Jeff.")
        result = agent.run("What is my name?")

        assert result.output is not None
        assert re.search("jeff", result.output.to_text(), re.IGNORECASE)
