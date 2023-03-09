from marshmallow import post_load, Schema, fields


class GoogleSheetsWriterToolSchema(Schema):
    auth_key_path = fields.Str(required=True)
    spreadsheet_key = fields.Str(required=True)
    worksheet_name = fields.Str()

    @post_load
    def make_tool(self, data, **kwargs):
        from warpspeed.tools import GoogleSheetsWriterTool

        return GoogleSheetsWriterTool(**data)
