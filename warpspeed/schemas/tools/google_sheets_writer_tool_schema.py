from marshmallow import post_load, fields
from warpspeed.schemas import BaseSchema


class GoogleSheetsWriterToolSchema(BaseSchema):
    auth_key_path = fields.Str(required=True)
    spreadsheet_key = fields.Str(required=True)
    worksheet_name = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from warpspeed.tools import GoogleSheetsWriterTool

        return GoogleSheetsWriterTool(**data)
