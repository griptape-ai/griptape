from marshmallow import fields, post_load
from griptape.schemas import BaseEventSchema, PolymorphicSchema


class StartTaskEventSchema(BaseEventSchema):
    task = fields.Nested(PolymorphicSchema())

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.events import StartTaskEvent 

        return StartTaskEvent(**data)
