from abc import abstractmethod
from marshmallow import fields
from griptape.schemas import BaseSchema, PolymorphicSchema


class BaseTaskSchema(BaseSchema):
    id = fields.Str()
    state = fields.Method("get_state")
    parent_ids = fields.List(fields.Str())
    child_ids = fields.List(fields.Str())

    output = fields.Nested(PolymorphicSchema()) 

    input = fields.Nested(PolymorphicSchema())
    
    type = fields.Str()

    @abstractmethod
    def make_obj(self, data, **kwargs):
        ...

    def get_state(self, obj):
        return obj.state.value
