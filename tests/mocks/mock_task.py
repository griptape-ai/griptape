from attr import define
from griptape.artifacts import TextArtifact
from griptape.tasks import BaseTask


@define
class MockTask(BaseTask):
    def input(self) -> TextArtifact:
        return TextArtifact("foo")
    
    def run(self) -> TextArtifact:
        return TextArtifact(self.input.to_text())

    def to_dict(self) -> dict:
        return {}
