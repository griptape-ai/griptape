from abc import abstractmethod
from marshmallow import fields, Schema
from marshmallow_enum import EnumField
from warpspeed.steps import Step


class StepSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Str(required=True)
    state = EnumField(Step.State)
    parent_ids = fields.List(fields.Str())
    child_ids = fields.List(fields.Str())

    @abstractmethod
    def make_step(self, data, **kwargs):
        ...
