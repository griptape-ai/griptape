from marshmallow import fields, post_load
from griptape.schemas import BaseEventSchema


class CompletionChunkEventSchema(BaseEventSchema):
    token = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.events import CompletionChunkEvent

        return CompletionChunkEvent(**data)
