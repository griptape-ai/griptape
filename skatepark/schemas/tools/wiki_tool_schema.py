from marshmallow import post_load
from skatepark.schemas import BaseSchema


class WikiToolSchema(BaseSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from skatepark.tools import WikiTool

        return WikiTool(**data)
