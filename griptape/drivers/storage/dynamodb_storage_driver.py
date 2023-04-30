from uuid import uuid4
from typing import Optional
from boto3 import resource
from attr import define, field
from griptape.drivers import BaseStorageDriver


@define
class DynamoDbStorageDriver(BaseStorageDriver):
    aws_region: str = field(default=None, kw_only=True)
    table_name: str = field(default=None, kw_only=True)
    partition_key: str = field(default=None, kw_only=True)
    value_attribute_key: str = field(default=None, kw_only=True)
    extra_attributes: any = field(default={}, kw_only=True)

    table: any = field(init=False)

    def __attrs_post_init__(self):
        dynamodb = resource(
            "dynamodb",
            region_name=self.aws_region,
        )

        self.table = dynamodb.Table(self.table_name)

    def save(self, value: any) -> str:
        key = uuid4().hex

        self.table.put_item(
            Item={
                self.partition_key: key,
                self.value_attribute_key: value,
                **self.extra_attributes,
            }
        )

        return key

    def load(self, key: str) -> Optional[any]:
        response = self.table.get_item(Key={self.partition_key: key})

        if "Item" in response:
            return response["Item"][self.value_attribute_key]
        return None

    def delete(self, key: str) -> None:
        self.table.delete_item(Key={self.partition_key: key})
