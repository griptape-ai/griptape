from marshmallow import post_load
from griptape.schemas import BasePromptEventSchema


class FinishPromptEventSchema(BasePromptEventSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.events import FinishPromptEvent

        return FinishPromptEvent(**data)
