from griptape.artifacts import TextArtifact
from griptape.utils import CommandRunner


class TestCommandRunner:
    def test_run(self):
        assert CommandRunner().run("echo 'test'").value == "test"
