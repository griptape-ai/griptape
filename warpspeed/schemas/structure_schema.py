from abc import abstractmethod
from marshmallow import Schema, fields
from warpspeed.schemas import PolymorphicSchema, RuleSchema


class StructureSchema(Schema):
    class Meta:
        ordered = True

    prompt_driver = fields.Nested(PolymorphicSchema())
    rules = fields.List(fields.Nested(RuleSchema()))
    steps = fields.List(fields.Nested(PolymorphicSchema()))

    @abstractmethod
    def make_structure(self, data, **kwargs):
        ...
