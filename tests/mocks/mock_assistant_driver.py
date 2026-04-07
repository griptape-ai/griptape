from __future__ import annotations

from attrs import define, field

from griptape.artifacts import BaseArtifact, InfoArtifact, TextArtifact
from griptape.drivers.assistant import BaseAssistantDriver


@define
class MockAssistantDriver(BaseAssistantDriver):
    mock_output: str = field(default="mock output", kw_only=True)

    def try_run(self, *args: BaseArtifact) -> BaseArtifact | InfoArtifact:
        return TextArtifact(self.mock_output)
