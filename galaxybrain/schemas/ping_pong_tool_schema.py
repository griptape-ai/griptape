from marshmallow import post_load, Schema


class PingPongToolSchema(Schema):
    @post_load
    def make_tool(self, data, **kwargs):
        from galaxybrain.tools import PingPongTool

        return PingPongTool(**data)
