from __future__ import annotations
import json
import logging
from typing import TYPE_CHECKING, Union
import inspect
import os
from abc import ABC, abstractmethod
from griptape.artifacts import BaseArtifact, TextArtifact

if TYPE_CHECKING:
    from griptape.core import BaseTool


class BaseExecutor(ABC):
    def execute(self, tool_activity: callable, value: BaseArtifact) -> BaseArtifact:
        result = self.before_execute(tool_activity, value)
        result = self.executor_result_to_artifact(
            self.try_execute(tool_activity, result)
        )
        result = self.after_execute(tool_activity, result)

        return result

    def before_execute(self, tool_activity: callable, value: BaseArtifact) -> BaseArtifact:
        for ramps in tool_activity.__self__.ramps.get(tool_activity.config["name"], []):
            value = ramps.process_input(tool_activity, value)

        return value

    def after_execute(self, tool_activity: callable, value: BaseArtifact) -> BaseArtifact:
        for ramps in tool_activity.__self__.ramps.get(tool_activity.config["name"], []):
            value = ramps.process_output(tool_activity, value)

        return value

    def executor_result_to_artifact(self, result: Union[BaseArtifact, str]) -> BaseArtifact:
        if isinstance(result, BaseArtifact):
            return result
        else:
            try:
                return BaseArtifact.from_dict(json.loads(result))
            except Exception:
                logging.exception("Error converting executor result to an artifact; defaulting to TextArtifact")

                return TextArtifact(result)

    @abstractmethod
    def try_execute(self, tool_activity: callable, value: BaseArtifact) -> Union[BaseArtifact, str]:
        ...

    def tool_dir(self, tool: BaseTool):
        class_file = inspect.getfile(tool.__class__)

        return os.path.dirname(os.path.abspath(class_file))
