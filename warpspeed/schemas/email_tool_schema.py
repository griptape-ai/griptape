from marshmallow import post_load, Schema, fields


class EmailToolSchema(Schema):
    host = fields.Str(required=True)
    port = fields.Int(required=True)
    from_email = fields.Str(required=True)
    use_ssl = fields.Bool()

    @post_load
    def make_tool(self, data, **kwargs):
        from warpspeed.tools import EmailTool

        return EmailTool(**data)
