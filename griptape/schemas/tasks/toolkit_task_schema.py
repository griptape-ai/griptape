from __future__ import annotations
from marshmallow import post_load, fields
from griptape.schemas import PromptTaskSchema, ActionSubtaskSchema


class ToolkitTaskSchema(PromptTaskSchema):
    max_subtasks = fields.Integer()
    subtasks = fields.List(fields.Nested(ActionSubtaskSchema))

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.tasks import ToolkitTask

        return ToolkitTask(**data)
