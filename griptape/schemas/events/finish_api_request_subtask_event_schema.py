from marshmallow import post_load
from griptape.schemas import BaseApiRequestSubtaskEventSchema


class FinishApiRequestSubtaskEventSchema(BaseApiRequestSubtaskEventSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.events import FinishApiRequestSubtaskEvent

        return FinishApiRequestSubtaskEvent(**data)
