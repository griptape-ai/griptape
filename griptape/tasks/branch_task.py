from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from attrs import define, field

from griptape.tasks.base_text_input_task import BaseTextInputTask

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact, TextArtifact


@define
class BranchTask(BaseTextInputTask):
    branch_fn: Callable[[BranchTask], TextArtifact] = field(kw_only=True)

    def run(self) -> BaseArtifact:
        return self.branch_fn(self)
