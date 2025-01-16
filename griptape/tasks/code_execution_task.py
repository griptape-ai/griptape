from __future__ import annotations

import functools
from typing import Callable, TypeVar

from attrs import define, field
from typing_extensions import ParamSpec

from griptape.artifacts import GenericArtifact
from griptape.artifacts.base_artifact import BaseArtifact
from griptape.tasks.base_text_input_task import BaseTextInputTask

A = TypeVar("A", bound=BaseArtifact)


P = ParamSpec("P")
R = TypeVar("R")


@define
class CodeExecutionTask(BaseTextInputTask[A]):
    on_run: Callable[[CodeExecutionTask[A]], A] = field(kw_only=True)

    def try_run(self) -> A:
        return self.on_run(self)

    @classmethod
    def wrap(cls, func: Callable[P, R]) -> Callable[P, CodeExecutionTask[GenericArtifact[R]]]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> CodeExecutionTask[GenericArtifact[R]]:
            def on_run(task: CodeExecutionTask[GenericArtifact[R]]) -> GenericArtifact[R]:
                output = func(**args, **kwargs)
                return GenericArtifact(output)

            return CodeExecutionTask(id=func.__name__, on_run=on_run)

        return wrapper
