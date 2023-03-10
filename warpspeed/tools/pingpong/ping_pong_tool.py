from warpspeed.tools import Tool
from attrs import define


@define
class PingPongTool(Tool):
    def run(self, value: any) -> str:
        return value
