from marshmallow import fields, post_load
from skatepark.schemas import PolymorphicSchema, StepSchema


class ToolkitStepSchema(StepSchema):
    prompt_template = fields.Str(required=True)
    max_substeps = fields.Int(allow_none=True)
    tools = fields.List(fields.Nested(PolymorphicSchema()), required=True)
    context = fields.Dict(keys=fields.Str(), values=fields.Raw())
    driver = fields.Nested(PolymorphicSchema(), allow_none=True)

    @post_load
    def make_obj(self, data, **kwargs):
        from skatepark.steps import ToolkitStep

        return ToolkitStep(**data)
