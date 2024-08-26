import boto3
import pytest
from moto import mock_dynamodb

from griptape.drivers import AmazonDynamoDbConversationMemoryDriver
from griptape.memory.structure import ConversationMemory
from griptape.structures import Pipeline
from griptape.tasks import PromptTask
from tests.utils.aws import mock_aws_credentials


class TestDynamoDbConversationMemoryDriver:
    DYNAMODB_TABLE_NAME = "griptape"
    DYNAMODB_PARTITION_KEY = "entryId"
    AWS_REGION = "us-west-2"
    VALUE_ATTRIBUTE_KEY = "foo"
    PARTITION_KEY_VALUE = "bar"

    @pytest.fixture(autouse=True)
    def _run_before_and_after_tests(self):
        mock_aws_credentials()
        self.mock_dynamodb = mock_dynamodb()
        self.mock_dynamodb.start()

        dynamodb = boto3.Session(region_name=self.AWS_REGION).client("dynamodb")
        dynamodb.create_table(
            TableName=self.DYNAMODB_TABLE_NAME,
            KeySchema=[{"AttributeName": self.DYNAMODB_PARTITION_KEY, "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": self.DYNAMODB_PARTITION_KEY, "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        yield

        dynamodb.delete_table(TableName=self.DYNAMODB_TABLE_NAME)
        self.mock_dynamodb.stop()

    def test_store(self):
        session = boto3.Session(region_name=self.AWS_REGION)
        dynamodb = session.resource("dynamodb")
        table = dynamodb.Table(self.DYNAMODB_TABLE_NAME)
        memory_driver = AmazonDynamoDbConversationMemoryDriver(
            session=session,
            table_name=self.DYNAMODB_TABLE_NAME,
            partition_key=self.DYNAMODB_PARTITION_KEY,
            value_attribute_key=self.VALUE_ATTRIBUTE_KEY,
            partition_key_value=self.PARTITION_KEY_VALUE,
        )
        memory = ConversationMemory(conversation_memory_driver=memory_driver)
        pipeline = Pipeline(conversation_memory=memory)

        pipeline.add_task(PromptTask("test"))

        response = table.get_item(TableName=self.DYNAMODB_TABLE_NAME, Key={"entryId": "bar"})
        assert "Item" not in response

        pipeline.run()

        response = table.get_item(TableName=self.DYNAMODB_TABLE_NAME, Key={"entryId": "bar"})
        assert "Item" in response

    def test_store_with_sort_key(self):
        session = boto3.Session(region_name=self.AWS_REGION)
        dynamodb = session.resource("dynamodb")
        table = dynamodb.Table(self.DYNAMODB_TABLE_NAME)
        memory_driver = AmazonDynamoDbConversationMemoryDriver(
            session=session,
            table_name=self.DYNAMODB_TABLE_NAME,
            partition_key=self.DYNAMODB_PARTITION_KEY,
            value_attribute_key=self.VALUE_ATTRIBUTE_KEY,
            partition_key_value=self.PARTITION_KEY_VALUE,
            sort_key="sortKey",
            sort_key_value="foo",
        )
        memory = ConversationMemory(conversation_memory_driver=memory_driver)
        pipeline = Pipeline(conversation_memory=memory)

        pipeline.add_task(PromptTask("test"))

        response = table.get_item(TableName=self.DYNAMODB_TABLE_NAME, Key={"entryId": "bar", "sortKey": "foo"})
        assert "Item" not in response

        pipeline.run()

        response = table.get_item(TableName=self.DYNAMODB_TABLE_NAME, Key={"entryId": "bar", "sortKey": "foo"})
        assert "Item" in response

    def test_load(self):
        memory_driver = AmazonDynamoDbConversationMemoryDriver(
            session=boto3.Session(region_name=self.AWS_REGION),
            table_name=self.DYNAMODB_TABLE_NAME,
            partition_key=self.DYNAMODB_PARTITION_KEY,
            value_attribute_key=self.VALUE_ATTRIBUTE_KEY,
            partition_key_value=self.PARTITION_KEY_VALUE,
        )
        memory = ConversationMemory(conversation_memory_driver=memory_driver, meta={"foo": "bar"})
        pipeline = Pipeline(conversation_memory=memory)

        pipeline.add_task(PromptTask("test"))

        pipeline.run()
        pipeline.run()

        runs, metadata = memory_driver.load()

        assert len(runs) == 2
        assert metadata == {"foo": "bar"}

    def test_load_with_sort_key(self):
        memory_driver = AmazonDynamoDbConversationMemoryDriver(
            session=boto3.Session(region_name=self.AWS_REGION),
            table_name=self.DYNAMODB_TABLE_NAME,
            partition_key=self.DYNAMODB_PARTITION_KEY,
            value_attribute_key=self.VALUE_ATTRIBUTE_KEY,
            partition_key_value=self.PARTITION_KEY_VALUE,
            sort_key="sortKey",
            sort_key_value="foo",
        )
        memory = ConversationMemory(conversation_memory_driver=memory_driver, meta={"foo": "bar"})
        pipeline = Pipeline(conversation_memory=memory)

        pipeline.add_task(PromptTask("test"))

        pipeline.run()
        pipeline.run()

        runs, metadata = memory_driver.load()

        assert len(runs) == 2
        assert metadata == {"foo": "bar"}
