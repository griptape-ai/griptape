from typing import Optional
import gspread
from attrs import define, field
from gspread.utils import ValueInputOption
from warpspeed.tools import Tool


@define
class GoogleSheetsWriterTool(Tool):
    auth_key_path: str = field(kw_only=True)
    spreadsheet_key: str = field(kw_only=True)
    worksheet_name: Optional[str] = field(default=None, kw_only=True)

    def run(self, args: dict[str]) -> str:
        action = args.get("action")

        try:
            return self.__execute_action(action, args)
        except Exception as e:
            return f"error interacting with sheet: {e}"

    def __execute_action(self, action: str, args: dict[str]) -> str:
        gc = gspread.service_account(filename=self.auth_key_path)
        spreadsheet = gc.open_by_key(self.spreadsheet_key)

        if self.worksheet_name is None:
            worksheet = spreadsheet.sheet1
        else:
            worksheet = spreadsheet.worksheet(self.worksheet_name)

        if action == "batch_update":
            ranges = args.get("ranges")

            worksheet.batch_update(
                ranges,
                value_input_option=ValueInputOption.user_entered
            )

            return "cells were successfully updated"
        return "invalid action name"
