from marshmallow import post_load, fields

from griptape.schemas.events.base_image_generation_event_schema import BaseImageGenerationEventSchema


class StartImageGenerationEventSchema(BaseImageGenerationEventSchema):
    prompts = fields.List(fields.Str())
    negative_prompts = fields.List(fields.Str())

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.events import StartImageGenerationEvent

        return StartImageGenerationEvent(**data)
