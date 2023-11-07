from marshmallow import post_load
from griptape.schemas import BaseActionSubtaskEventSchema


class StartActionSubtaskEventSchema(BaseActionSubtaskEventSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.events import StartActionSubtaskEvent

        return StartActionSubtaskEvent(**data)
