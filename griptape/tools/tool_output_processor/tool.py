from __future__ import annotations
from attr import define
from griptape.mixins import TextMemoryActivitiesMixin
from griptape.tools import BaseTool


@define
class ToolOutputProcessor(BaseTool, TextMemoryActivitiesMixin):
    ...
