from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.artifacts.list_artifact import ListArtifact
from griptape.tasks.prompt_task import PromptTask

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact
    from griptape.drivers import BaseAssistantDriver


@define
class AssistantTask(PromptTask):
    """Task to run a AssistantTask.

    Attributes:
        driver: Driver to run the Structure.
    """

    driver: BaseAssistantDriver = field(kw_only=True)

    def try_run(self) -> BaseArtifact:
        if isinstance(self.input, ListArtifact):
            return self.driver.run(*self.input.value)
        else:
            return self.driver.run(self.input)
