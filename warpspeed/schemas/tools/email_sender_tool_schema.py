from marshmallow import post_load, fields
from warpspeed.schemas import BaseSchema


class EmailSenderToolSchema(BaseSchema):
    host = fields.Str(required=True)
    port = fields.Int(required=True)
    from_email = fields.Str(required=True)
    use_ssl = fields.Bool()

    @post_load
    def make_obj(self, data, **kwargs):
        from warpspeed.tools import EmailSenderTool

        return EmailSenderTool(**data)
