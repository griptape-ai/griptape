from marshmallow import post_load
from warpspeed.schemas import BaseSchema


class WikiToolSchema(BaseSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from warpspeed.tools import WikiTool

        return WikiTool(**data)
