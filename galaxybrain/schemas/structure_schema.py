from abc import abstractmethod
from marshmallow import Schema, fields
from galaxybrain.schemas import PolymorphicSchema, RuleSchema


class StructureSchema(Schema):
    prompt_driver = fields.Nested(PolymorphicSchema())
    steps = fields.List(fields.Nested(PolymorphicSchema()))
    rules = fields.List(fields.Nested(RuleSchema()))

    @abstractmethod
    def make_structure(self, data, **kwargs):
        ...
