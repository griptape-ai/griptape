from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.tasks import BaseTextInputTask

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact
    from griptape.drivers import BaseAssistantDriver


@define
class AssistantTask(BaseTextInputTask):
    """Task to run a AssistantTask.

    Attributes:
        driver: Driver to run the Structure.
    """

    driver: BaseAssistantDriver = field(kw_only=True)

    def try_run(self) -> BaseArtifact:
        return self.driver.run(self.input)
