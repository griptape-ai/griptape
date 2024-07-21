from attrs import define

from griptape.artifacts import TextArtifact
from griptape.tasks import BaseMultiTextInputTask


@define
class MockMultiTextInputTask(BaseMultiTextInputTask):
    def run(self) -> TextArtifact:
        return TextArtifact(self.input[0].to_text())
