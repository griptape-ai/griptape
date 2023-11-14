from marshmallow import fields
from griptape.schemas import BaseTaskEventSchema


class BaseActionSubtaskEventSchema(BaseTaskEventSchema):
    subtask_parent_task_id = fields.Str()
    subtask_thought = fields.Str()
    subtask_action_name = fields.Str()
    subtask_action_path = fields.Str()
    subtask_action_input = fields.Dict()
