from warpspeed.tools import Tool
from attrs import define


@define(frozen=True)
class PingPongTool(Tool):
    def run(self, value: any) -> str:
        return value
