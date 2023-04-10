from typing import Optional
from attr import define, field
from griptape.core import BaseTool
from skatepark.steps import BaseToolStep


@define
class ToolkitStep(BaseToolStep):
    tool_names: list[str] = field(kw_only=True)

    def find_tool(self, tool_name: str) -> Optional[BaseTool]:
        for tool in self.tool_names:
            if tool == tool_name:
                # TODO: load tool
                pass

        return None
