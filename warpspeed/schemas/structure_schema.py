from abc import abstractmethod
from marshmallow import fields
from warpspeed.schemas import PolymorphicSchema, RuleSchema, BaseSchema


class StructureSchema(BaseSchema):
    class Meta:
        ordered = True

    id = fields.Str()
    type = fields.Str(required=True)
    prompt_driver = fields.Nested(PolymorphicSchema())
    rules = fields.List(fields.Nested(RuleSchema()))
    steps = fields.List(fields.Nested(PolymorphicSchema()))

    @abstractmethod
    def make_obj(self, data, **kwargs):
        ...
