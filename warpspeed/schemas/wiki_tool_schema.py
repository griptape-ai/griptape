from marshmallow import post_load, Schema


class WikiToolSchema(Schema):
    @post_load
    def make_tool(self, data, **kwargs):
        from warpspeed.tools import WikiTool

        return WikiTool(**data)
