from attrs import define, field

from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.tasks import BaseTask


@define
class MockTask(BaseTask):
    mock_input: str = field(default="foobar")

    @property
    def input(self) -> BaseArtifact:
        return TextArtifact(self.mock_input)

    def run(self) -> BaseArtifact:
        return self.input
