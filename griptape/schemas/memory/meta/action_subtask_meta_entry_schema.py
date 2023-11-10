from marshmallow import fields, post_load
from griptape.schemas import BaseSchema


class ActionSubtaskMetaEntrySchema(BaseSchema):
    thought = fields.Str()
    action = fields.Str()
    answer = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.memory.meta import ActionSubtaskMetaEntry

        return ActionSubtaskMetaEntry(**data)
