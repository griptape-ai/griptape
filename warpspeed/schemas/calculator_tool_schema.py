from marshmallow import post_load
from warpspeed.schemas import BaseSchema


class CalculatorToolSchema(BaseSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from warpspeed.tools import CalculatorTool

        return CalculatorTool(**data)
