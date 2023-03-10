from marshmallow import post_load, fields
from warpspeed.schemas import BaseSchema


class SqlClientToolSchema(BaseSchema):
    engine_url = fields.Str(required=True)
    engine_hint = fields.Str(required=True)

    @post_load
    def make_obj(self, data, **kwargs):
        from warpspeed.tools import SqlClientTool

        return SqlClientTool(**data)
