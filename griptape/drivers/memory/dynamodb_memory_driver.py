from attr import define, field
from griptape.drivers import BaseMemoryDriver
from griptape.memory.structure import ConversationMemory
from boto3 import resource


@define
class DynamoDbMemoryDriver(BaseMemoryDriver):
    aws_region: str = field(default=None, kw_only=True)
    table_name: str = field(default=None, kw_only=True)
    partition_key: str = field(default=None, kw_only=True)
    value_attribute_key: str = field(default=None, kw_only=True)
    partition_key_value: str = field(default=None, kw_only=True)

    table: any = field(init=False)

    def __attrs_post_init__(self):
        dynamodb = resource(
            "dynamodb",
            region_name=self.aws_region,
        )

        self.table = dynamodb.Table(self.table_name)

    def store(self, memory: ConversationMemory) -> None:
        self.table.update_item(
            Key={
                self.partition_key: self.partition_key_value,
            },
            UpdateExpression='set #attr = :value',
            ExpressionAttributeNames={
                '#attr': self.value_attribute_key,
            },
            ExpressionAttributeValues={
                ':value': memory.to_json(),
            }
        )

    def load(self) -> ConversationMemory:
        response = self.table.get_item(
            Key={self.partition_key: self.partition_key_value}
        )

        if "Item" in response and self.value_attribute_key in response["Item"]:
            memory_value = response["Item"][self.value_attribute_key]

            memory = ConversationMemory.from_json(memory_value)

            memory.driver = self

            return memory
        return None
