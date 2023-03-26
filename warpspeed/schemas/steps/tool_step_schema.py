from marshmallow import fields, post_load
from warpspeed.schemas import PolymorphicSchema, StepSchema


class ToolStepSchema(StepSchema):
    prompt_template = fields.Str(required=True)
    max_substeps = fields.Int()
    tool = fields.Nested(PolymorphicSchema(), required=True)
    context = fields.Dict(keys=fields.Str(), values=fields.Raw())
    driver = fields.Nested(PolymorphicSchema(), allow_none=True)

    @post_load
    def make_obj(self, data, **kwargs):
        from warpspeed.steps import ToolStep

        return ToolStep(**data)
