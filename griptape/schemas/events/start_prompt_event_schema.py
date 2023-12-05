from marshmallow import post_load
from griptape.schemas import BasePromptEventSchema


class StartPromptEventSchema(BasePromptEventSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.events import StartPromptEvent

        return StartPromptEvent(**data)
