from griptape.executors import DockerExecutor


class TestDockerExecutor:
    def test_init(self):
        assert isinstance(DockerExecutor(), DockerExecutor)
