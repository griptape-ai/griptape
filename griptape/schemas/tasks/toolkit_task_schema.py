from marshmallow import fields, post_load
from griptape.schemas import PolymorphicSchema, TaskSchema


class ToolkitTaskSchema(TaskSchema):
    prompt_template = fields.Str(required=True)
    max_subtasks = fields.Int(allow_none=True)
    tool_names = fields.List(fields.Str(), required=True)
    context = fields.Dict(keys=fields.Str(), values=fields.Raw())
    driver = fields.Nested(PolymorphicSchema(), allow_none=True)

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.tasks import ToolkitTask

        return ToolkitTask(**data)
