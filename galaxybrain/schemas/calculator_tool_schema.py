from marshmallow import post_load, Schema


class CalculatorToolSchema(Schema):
    @post_load
    def make_tool(self, data, **kwargs):
        from galaxybrain.tools import CalculatorTool

        return CalculatorTool(**data)
