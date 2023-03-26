from marshmallow import post_load, fields
from warpspeed.schemas import BaseSchema


class DataScientistToolSchema(BaseSchema):
    libs = fields.Dict(keys=fields.Str(), values=fields.Str())

    @post_load
    def make_obj(self, data, **kwargs):
        from warpspeed.tools import DataScientistTool

        return DataScientistTool(**data)
