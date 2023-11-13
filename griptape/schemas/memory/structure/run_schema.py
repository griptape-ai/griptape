from marshmallow import fields, post_load
from griptape.schemas import BaseSchema


class RunSchema(BaseSchema):
    id = fields.Str()
    input = fields.Str()
    output = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.memory.structure import Run

        return Run(**data)
