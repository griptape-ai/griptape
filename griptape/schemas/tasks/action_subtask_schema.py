from marshmallow import fields, post_load
from griptape.schemas import TextArtifactSchema
from .prompt_task_schema import PromptTaskSchema


class ActionSubtaskSchema(PromptTaskSchema):
    parent_task_id = fields.Str()
    thought = fields.Str()
    action_type = fields.Str()
    action_name = fields.Str()
    action_activity = fields.Str()
    action_input = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.tasks import ActionSubtask

        return ActionSubtask(**data)
