from typing import Optional
from attr import define, field
from griptape.core import BaseTool, BaseExecutor
from griptape.core.executors import LocalExecutor


@define
class ToolLoader:
    tools: list[BaseTool] = field(factory=list, kw_only=True)
    executor: BaseExecutor = field(default=LocalExecutor(), kw_only=True)

    @tools.validator
    def validate_tools(self, _, tools) -> None:
        tool_names = [t.name for t in tools]

        if len(tool_names) > len(set(tool_names)):
            raise ValueError("tools have to be unique")

    def load_tool(self, tool_name: str) -> Optional[BaseTool]:
        return next((t for t in self.tools if t.name == tool_name), None)
