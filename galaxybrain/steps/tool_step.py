from __future__ import annotations
from typing import Optional
from attrs import define, field
from galaxybrain.tools import Tool
from galaxybrain.steps import BaseToolStep


@define
class ToolStep(BaseToolStep):
    tool: Tool = field(kw_only=True)

    def find_tool(self, action_name: str) -> Optional[Tool]:
        if self.tool.name == action_name:
            return self.tool
        else:
            return None
