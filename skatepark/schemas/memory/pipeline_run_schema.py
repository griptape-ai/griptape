from marshmallow import fields, post_load
from skatepark.schemas import BaseSchema


class PipelineRunSchema(BaseSchema):
    class Meta:
        ordered = True

    id = fields.Str()
    input = fields.Str()
    output = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from skatepark.memory import PipelineRun

        return PipelineRun(**data)
