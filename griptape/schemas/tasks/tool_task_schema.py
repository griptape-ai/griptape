from __future__ import annotations
from marshmallow import post_load, fields
from griptape.schemas import PromptTaskSchema, ActionSubtaskSchema


class ToolTaskSchema(PromptTaskSchema):
    subtask = fields.Nested(ActionSubtaskSchema)

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.tasks import ToolTask

        return ToolTask(**data)
