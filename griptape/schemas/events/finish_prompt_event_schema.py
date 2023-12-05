from marshmallow import post_load, fields
from griptape.schemas import BasePromptEventSchema


class FinishPromptEventSchema(BasePromptEventSchema):
    result = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.events import FinishPromptEvent

        return FinishPromptEvent(**data)
