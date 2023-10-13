from abc import abstractmethod
from marshmallow import fields
from .base_task_schema import BaseTaskSchema


class BaseTextInputTaskSchema(BaseTaskSchema):
    input_template = fields.Str()
    context = fields.Dict()

    @abstractmethod
    def make_obj(self, data, **kwargs):
        ...
