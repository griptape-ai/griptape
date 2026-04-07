from griptape.artifacts import InfoArtifact


class TestInfoArtifact:
    def test_value_type_conversion(self):
        assert InfoArtifact("1").value == "1"
        assert InfoArtifact(1).value == "1"

    def test_to_text(self):
        assert InfoArtifact("foobar").to_text() == "foobar"

    def test_to_dict(self):
        assert InfoArtifact("foobar").to_dict()["value"] == "foobar"
