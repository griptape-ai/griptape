from griptape.artifacts import InfoArtifact


class TestInfoArtifact:
    def test_to_text(self):
        assert InfoArtifact("foobar").to_text() == "foobar"

    def test_to_dict(self):
        assert InfoArtifact("foobar").to_dict()["value"] == "foobar"
