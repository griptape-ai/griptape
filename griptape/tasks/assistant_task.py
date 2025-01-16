from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.artifacts.text_artifact import TextArtifact
from griptape.tasks import BaseTextInputTask

if TYPE_CHECKING:
    from griptape.drivers.assistant import BaseAssistantDriver


@define
class AssistantTask(BaseTextInputTask[TextArtifact]):
    """Task to run an Assistant.

    Attributes:
        assistant_driver: Driver to run the Assistant.
    """

    assistant_driver: BaseAssistantDriver = field(kw_only=True)

    def try_run(self) -> TextArtifact:
        return self.assistant_driver.run(self.input)
