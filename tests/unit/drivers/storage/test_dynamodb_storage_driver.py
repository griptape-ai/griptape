import pytest
from boto3 import resource
from moto import mock_dynamodb
from griptape.drivers import DynamoDBStorageDriver


class TestDynamoDBStorageDriver:
    @pytest.fixture(autouse=True)
    @mock_dynamodb
    def driver_gen(self):
        dynamodb = resource("dynamodb", region_name="us-west-2")
        driver = DynamoDBStorageDriver(
            aws_region="us-west-2",
            table_name="griptape",
            partition_key="entryId",
            value_attribute_key="value",
            extra_attributes={
                "foo": "bar",
            },
        )

        dynamodb.create_table(
            TableName=driver.table_name,
            KeySchema=[{"AttributeName": driver.partition_key, "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": driver.partition_key, "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        yield driver

        dynamodb.delete_table(TableName=driver.table_name)

    @mock_dynamodb
    def test_save(self, driver_gen):
        driver = next(driver_gen)
        key = driver.save("foo")

        assert driver.load(key) == "foo"

    @mock_dynamodb
    def test_load(self, driver_gen):
        driver = next(driver_gen)
        key = driver.save("foo")

        assert driver.load(key) == "foo"
        assert driver.load("empty") is None

    @mock_dynamodb
    def test_delete(self, driver_gen):
        driver = next(driver_gen)
        key = driver.save("foo")

        driver.delete(key)

        assert driver.load(key) is None
        assert driver.delete(key) is None
