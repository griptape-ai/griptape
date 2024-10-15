from functools import cached_property

from attrs import define, field

from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.tasks import BaseTask


@define
class MockTask(BaseTask):
    mock_input: str = field(default="foobar")

    @cached_property
    def input(self) -> BaseArtifact:
        return TextArtifact(self.mock_input)

    def try_run(self) -> BaseArtifact:
        return self.input
