import re
from typing import Optional, Union
from attrs import define, field
import gspread
from warpspeed.tools import Tool


@define
class GoogleSheetsReaderTool(Tool):
    auth_key_path: str = field(kw_only=True)
    spreadsheet_key: str = field(kw_only=True)
    worksheet_name: Optional[str] = field(default=None, kw_only=True)

    def run(self, args: dict[str]) -> str:
        action = args.get("action")

        try:
            return self.__execute_action(action, args)
        except Exception as e:
            return f"error interacting with sheet: {e}"

    def __execute_action(self, action: str, args: dict[str]) -> Union[str, list[str]]:
        gc = gspread.service_account(filename=self.auth_key_path, scopes=gspread.auth.READONLY_SCOPES)
        spreadsheet = gc.open_by_key(self.spreadsheet_key)

        if self.worksheet_name is None:
            worksheet = spreadsheet.sheet1
        else:
            worksheet = spreadsheet.worksheet(self.worksheet_name)

        if action == "get_values":
            return worksheet.get_values(args.get("range"))
        elif action == "search":
            return [f"cell {cell.address}: {cell.value}" for cell in worksheet.findall(re.compile(args.get("regex")))]
        return "invalid action name"
