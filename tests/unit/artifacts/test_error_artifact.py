from griptape.artifacts import ErrorArtifact


class TestErrorArtifact:
    def test_to_text(self):
        assert ErrorArtifact("foobar").to_text() == "foobar"
