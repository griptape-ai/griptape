from marshmallow import post_load, Schema


class CalculatorToolSchema(Schema):
    @post_load
    def make_tool(self, data, **kwargs):
        from warpspeed.tools import CalculatorTool

        return CalculatorTool(**data)
