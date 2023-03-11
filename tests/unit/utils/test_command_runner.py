from warpspeed.utils import CommandRunner


class TestCommandRunner:
    def test_run(self):
        assert CommandRunner().run("echo 'test'") == "test"
