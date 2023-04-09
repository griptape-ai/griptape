from warpspeed.tools import Tool
from attr import define


@define
class PingPongTool(Tool):
    def run(self, value: any) -> str:
        return value
