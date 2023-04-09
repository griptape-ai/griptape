from marshmallow import post_load, fields
from skatepark.schemas import BaseSchema


class DataScientistToolSchema(BaseSchema):
    libs = fields.Dict(keys=fields.Str(), values=fields.Str())

    @post_load
    def make_obj(self, data, **kwargs):
        from skatepark.tools import DataScientistTool

        return DataScientistTool(**data)
