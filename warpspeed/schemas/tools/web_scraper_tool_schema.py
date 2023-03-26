from marshmallow import post_load, fields
from warpspeed.schemas import BaseSchema


class WebScraperToolSchema(BaseSchema):
    include_links = fields.Bool()

    @post_load
    def make_obj(self, data, **kwargs):
        from warpspeed.tools import WebScraperTool

        return WebScraperTool(**data)
