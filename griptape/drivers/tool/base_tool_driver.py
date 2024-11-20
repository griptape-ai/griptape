from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from attrs import define

if TYPE_CHECKING:
    from griptape.tools.base_tool import BaseTool


@define
class BaseToolDriver(ABC):
    @abstractmethod
    def initialize_tool(self, tool: BaseTool) -> None:
        """Performs some initialization operations on the Tool. This method is intended to mutate the Tool object.

        Args:
            tool: Tool to initialize.

        """

    ...
