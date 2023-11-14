from __future__ import annotations
from marshmallow import post_load
from griptape.schemas import BaseEventSchema


class StartStructureRunEventSchema(BaseEventSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.events import StartStructureRunEvent

        return StartStructureRunEvent(**data)
