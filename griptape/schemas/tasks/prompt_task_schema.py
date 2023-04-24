from marshmallow import fields, post_load
from griptape.schemas import TaskSchema, PolymorphicSchema


class PromptTaskSchema(TaskSchema):
    prompt_template = fields.Str(required=True)
    context = fields.Dict(keys=fields.Str(), values=fields.Raw())
    driver = fields.Nested(PolymorphicSchema(), allow_none=True)

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.tasks import PromptTask

        return PromptTask(**data)
