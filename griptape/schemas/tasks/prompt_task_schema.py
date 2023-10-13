from marshmallow import fields, post_load
from griptape.schemas import PolymorphicSchema
from .base_text_input_task_schema import BaseTextInputTaskSchema


class PromptTaskSchema(BaseTextInputTaskSchema):
    output = fields.Nested(PolymorphicSchema(), dump_only=True)

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.tasks import PromptTask

        return PromptTask(**data)
