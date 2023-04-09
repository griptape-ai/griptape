from marshmallow import post_load, fields
from skatepark.schemas import BaseSchema


class GoogleSearchToolSchema(BaseSchema):
    results_count = fields.Int()
    lang = fields.Str()
    timeout = fields.Int()
    use_api = fields.Bool()
    api_search_key = fields.Str()
    api_search_id = fields.Str()
    api_country = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from skatepark.tools import GoogleSearchTool

        return GoogleSearchTool(**data)
