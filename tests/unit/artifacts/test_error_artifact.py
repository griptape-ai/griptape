from griptape.artifacts import ErrorArtifact


class TestErrorArtifact:
    def test_to_text(self):
        assert ErrorArtifact("foobar").to_text() == "foobar"

    def test_to_dict(self):
        assert ErrorArtifact("foobar").to_dict()["value"] == "foobar"
