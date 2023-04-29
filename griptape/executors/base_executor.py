from __future__ import annotations
from typing import TYPE_CHECKING
import inspect
import os
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from griptape.core import BaseTool


class BaseExecutor(ABC):
    def execute(self, tool_activity: callable, value: any) -> any:
        value = self.before_execute(tool_activity, value)
        result = self.try_execute(tool_activity, value)
        result = self.after_execute(tool_activity, result)

        return result

    def before_execute(self, tool_activity: callable, result: any) -> any:
        for middleware in tool_activity.__self__.middleware.get(tool_activity.config["name"], []):
            result = middleware.process_input(tool_activity, result)

        return result

    def after_execute(self, tool_activity: callable, result: any) -> any:
        for middleware in tool_activity.__self__.middleware.get(tool_activity.config["name"], []):
            result = middleware.process_output(tool_activity, result)

        return result

    @abstractmethod
    def try_execute(self, tool_activity: callable, value: any) -> any:
        ...

    def tool_dir(self, tool: BaseTool):
        class_file = inspect.getfile(tool.__class__)

        return os.path.dirname(os.path.abspath(class_file))
