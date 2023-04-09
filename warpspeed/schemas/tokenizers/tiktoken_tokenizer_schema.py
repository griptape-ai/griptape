from marshmallow import fields, post_load
from warpspeed.schemas import BaseSchema


class TiktokenTokenizerSchema(BaseSchema):
    model = fields.Str()
    stop_sequence = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from warpspeed.utils import TiktokenTokenizer

        return TiktokenTokenizer(**data)
