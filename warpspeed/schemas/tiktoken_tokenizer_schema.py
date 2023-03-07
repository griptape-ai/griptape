from marshmallow import Schema, fields, post_load


class TiktokenTokenizerSchema(Schema):
    model = fields.Str()
    stop_token = fields.Str()

    @post_load
    def make_tokenizer(self, data, **kwargs):
        from warpspeed.utils import TiktokenTokenizer

        return TiktokenTokenizer(**data)
