from marshmallow import post_load
from warpspeed.schemas import BaseSchema


class AwsToolSchema(BaseSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from warpspeed.tools import AwsTool

        return AwsTool(**data)
