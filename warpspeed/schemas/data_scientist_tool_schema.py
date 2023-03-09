from marshmallow import post_load, Schema, fields


class DataScientistToolSchema(Schema):
    libs = fields.Dict(keys=fields.Str(), values=fields.Str())

    @post_load
    def make_tool(self, data, **kwargs):
        from warpspeed.tools import DataScientistTool

        return DataScientistTool(**data)
