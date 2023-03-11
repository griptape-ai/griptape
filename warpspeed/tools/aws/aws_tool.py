from warpspeed.tools import Tool
from warpspeed.utils import CommandRunner


class AwsTool(Tool):
    def run(self, command: str) -> str:
        result = CommandRunner().run(f"AWS_PAGER='' {command} --output json")
        result = "[]" if result == "" else result

        return result
