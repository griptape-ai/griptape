from attr import define, field
from griptape.artifacts import TextArtifact, BaseArtifact, ErrorArtifact
from griptape.tasks import BaseTextInputTask, BaseTask
from typing import Callable


@define
class PythonTask(BaseTextInputTask):
    run_fn: Callable[[BaseTask], BaseArtifact] = field(kw_only=True)

    def run(self) -> BaseArtifact:
        try:
            return self.run_fn(self)
        except Exception as e:
            return ErrorArtifact(f"error during Python Task execution: {e}")
