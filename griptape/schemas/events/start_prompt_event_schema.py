from marshmallow import fields, post_load
from griptape.schemas import BaseEventSchema


class StartPromptEventSchema(BaseEventSchema):
    token_count = fields.Int()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.events import StartPromptEvent

        return StartPromptEvent(**data)
