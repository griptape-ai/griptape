from abc import abstractmethod
from marshmallow import fields
from marshmallow_enum import EnumField
from griptape.schemas import BaseSchema
from griptape.tasks import BaseTask


class TaskSchema(BaseSchema):
    class Meta:
        ordered = True

    id = fields.Str()
    state = EnumField(BaseTask.State)
    parent_ids = fields.List(fields.Str())
    child_ids = fields.List(fields.Str())

    @abstractmethod
    def make_obj(self, data, **kwargs):
        ...
