from abc import abstractmethod
from marshmallow import fields, Schema


class StepSchema(Schema):
    id = fields.Str(required=True)
    parent_id = fields.Str(allow_none=True)
    child_id = fields.Str(allow_none=True)

    @abstractmethod
    def make_step(self, data, **kwargs):
        pass
