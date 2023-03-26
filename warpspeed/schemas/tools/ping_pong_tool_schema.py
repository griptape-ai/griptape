from marshmallow import post_load
from warpspeed.schemas import BaseSchema


class PingPongToolSchema(BaseSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from warpspeed.tools import PingPongTool

        return PingPongTool(**data)
