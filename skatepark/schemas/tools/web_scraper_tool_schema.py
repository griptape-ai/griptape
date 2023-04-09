from marshmallow import post_load, fields
from skatepark.schemas import BaseSchema


class WebScraperToolSchema(BaseSchema):
    include_links = fields.Bool()

    @post_load
    def make_obj(self, data, **kwargs):
        from skatepark.tools import WebScraperTool

        return WebScraperTool(**data)
