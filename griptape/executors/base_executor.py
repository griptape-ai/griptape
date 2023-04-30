from __future__ import annotations
import json
from typing import TYPE_CHECKING, Union
import inspect
import os
from abc import ABC, abstractmethod
from griptape.artifacts import BaseArtifact, TextOutput

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
        for middleware in tool_activity.__self__.middleware.get(tool_activity.config["name"], []):
            value = middleware.process_input(tool_activity, value)

        return value

    def after_execute(self, tool_activity: callable, value: BaseArtifact) -> BaseArtifact:
        for middleware in tool_activity.__self__.middleware.get(tool_activity.config["name"], []):
            value = middleware.process_output(tool_activity, value)

        return value

    def executor_result_to_artifact(self, result: Union[BaseArtifact, str]) -> BaseArtifact:
        if isinstance(result, BaseArtifact):
            return result
        else:
            try:
                from griptape.schemas import TextOutputSchema, ErrorOutputSchema

                result_dict = json.loads(result)

                if result_dict["type"] == "TextOutput":
                    return TextOutputSchema().load(result_dict)
                elif result_dict["type"] == "ErrorOutput":
                    return ErrorOutputSchema().load(result_dict)
                else:
                    return TextOutput(result)
            except Exception as e:
                return TextOutput(result)

    @abstractmethod
    def try_execute(self, tool_activity: callable, value: BaseArtifact) -> Union[BaseArtifact, str]:
        ...

    def tool_dir(self, tool: BaseTool):
        class_file = inspect.getfile(tool.__class__)

        return os.path.dirname(os.path.abspath(class_file))
