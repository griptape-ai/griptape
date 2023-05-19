from __future__ import annotations
import json
import logging
from typing import TYPE_CHECKING, Union, Optional
import inspect
import os
from abc import ABC, abstractmethod
from griptape.artifacts import BaseArtifact, InfoArtifact

if TYPE_CHECKING:
    from griptape.core import BaseTool


class BaseExecutor(ABC):
    def execute(self, tool_activity: callable, value: Optional[dict]) -> BaseArtifact:
        preprocessed_value = self.before_execute(tool_activity, value)

        artifact = self.executor_result_to_artifact(
            self.try_execute(tool_activity, preprocessed_value)
        )

        return self.after_execute(tool_activity, artifact)

    def before_execute(self, tool_activity: callable, value: Optional[dict]) -> Optional[dict]:
        for ramp in tool_activity.__self__.ramps.get(tool_activity.name, []):
            value = ramp.process_input(tool_activity, value)

        return value

    def after_execute(self, tool_activity: callable, value: Optional[BaseArtifact]) -> BaseArtifact:
        for ramp in tool_activity.__self__.ramps.get(tool_activity.name, []):
            value = ramp.process_output(tool_activity, value)

        return value

    @abstractmethod
    def try_execute(self, tool_activity: callable, value: Optional[dict]) -> Union[BaseArtifact, str]:
        ...

    def executor_result_to_artifact(self, result: Union[BaseArtifact, str]) -> BaseArtifact:
        if isinstance(result, BaseArtifact):
            return result
        else:
            try:
                return BaseArtifact.from_dict(json.loads(result))
            except Exception:
                logging.error("Error converting executor result to an artifact; defaulting to InfoArtifact")

                return InfoArtifact(result)

    def tool_dir(self, tool: BaseTool):
        class_file = inspect.getfile(tool.__class__)

        return os.path.dirname(os.path.abspath(class_file))
