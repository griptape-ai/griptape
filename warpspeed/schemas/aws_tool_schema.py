from marshmallow import post_load, fields
from warpspeed.schemas import BaseSchema


class AwsToolSchema(BaseSchema):
    policy = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from warpspeed.tools import AwsTool

        return AwsTool(**data)
