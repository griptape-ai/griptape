from marshmallow import fields
from griptape.schemas import BaseEventSchema, PolymorphicSchema


class BaseTaskEventSchema(BaseEventSchema):
    task_id = fields.Str()
    task_parent_ids = fields.List(fields.Str())
    task_child_ids = fields.List(fields.Str())
    task_input = fields.Nested(PolymorphicSchema())
    task_output = fields.Nested(PolymorphicSchema())
