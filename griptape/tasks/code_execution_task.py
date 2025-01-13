from __future__ import annotations

import functools
from typing import Any, Callable

from attrs import define, field

from griptape.artifacts import BaseArtifact
from griptape.tasks import BaseTask, BaseTextInputTask


@define
class CodeExecutionTask(BaseTextInputTask):
    on_run: Callable[[CodeExecutionTask], BaseArtifact] = field(kw_only=True)

    def __call__(self, *args, **kwargs) -> CodeExecutionTask:
        return self.wrap(*args, **kwargs)

    def try_run(self) -> BaseArtifact:
        return self.on_run(self)

    @classmethod
    def wrap(cls, func: Callable) -> Any:
        from griptape.artifacts import GenericArtifact

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            def on_run(task: Any) -> Any:
                # Any tasks must be "unwrapped" to get their output value
                arg_values = [arg.output.value for arg in args if isinstance(arg, BaseTask) if arg.output]
                output = func(*arg_values)

                if isinstance(output, BaseArtifact):
                    return output
                else:
                    return GenericArtifact(output)

            task = cls(id=func.__name__, on_run=on_run)

            for arg in args:
                if isinstance(arg, BaseTask):
                    task.add_parent(arg)

            return task

        return wrapper
