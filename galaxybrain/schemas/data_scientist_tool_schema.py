from marshmallow import post_load, Schema


class DataScientistToolSchema(Schema):
    @post_load
    def make_tool(self, data, **kwargs):
        from galaxybrain.tools import DataScientistTool

        return DataScientistTool(**data)
