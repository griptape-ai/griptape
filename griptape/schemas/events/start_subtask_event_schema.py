from marshmallow import fields, post_load
from griptape.schemas import BaseEventSchema, ActionSubtaskSchema


class StartSubtaskEventSchema(BaseEventSchema):
    subtask = fields.Nested(ActionSubtaskSchema)

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.events import StartSubtaskEvent 

        return StartSubtaskEvent(**data)
