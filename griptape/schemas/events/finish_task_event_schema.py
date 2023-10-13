from marshmallow import fields, post_load
from griptape.schemas import BaseEventSchema, PolymorphicSchema


class FinishTaskEventSchema(BaseEventSchema):
    task = fields.Nested(PolymorphicSchema())

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.events import FinishTaskEvent 

        return FinishTaskEvent(**data)
