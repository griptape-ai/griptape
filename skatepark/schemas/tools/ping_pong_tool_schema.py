from marshmallow import post_load
from skatepark.schemas import BaseSchema


class PingPongToolSchema(BaseSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from skatepark.tools import PingPongTool

        return PingPongTool(**data)
