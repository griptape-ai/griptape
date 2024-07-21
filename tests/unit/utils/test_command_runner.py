from griptape.utils import CommandRunner


class TestCommandRunner:
    def test_run(self):
        assert "test" in CommandRunner().run("echo 'test'").value
