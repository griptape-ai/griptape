from __future__ import annotations
from attr import define
from griptape.mixins import ToolMemoryActivitiesMixin
from griptape.tools import BaseTool


@define
class ToolOutputProcessor(BaseTool, ToolMemoryActivitiesMixin):
    ...
