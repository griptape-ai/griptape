from marshmallow import post_load, fields

from griptape.schemas.events.base_image_generation_event_schema import BaseImageGenerationEventSchema


class FinishImageGenerationEventSchema(BaseImageGenerationEventSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.events import FinishImageGenerationEvent

        return FinishImageGenerationEvent(**data)
