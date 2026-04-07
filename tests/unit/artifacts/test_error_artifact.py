from griptape.artifacts import ErrorArtifact


class TestErrorArtifact:
    def test_value_type_conversion(self):
        assert ErrorArtifact("1").value == "1"
        assert ErrorArtifact(1).value == "1"

    def test_to_text(self):
        assert ErrorArtifact("foobar").to_text() == "foobar"

    def test_to_dict(self):
        assert ErrorArtifact("foobar").to_dict()["value"] == "foobar"

    def test_exception_instance(self):
        assert isinstance(ErrorArtifact("foobar", exception=Exception("foobar")).exception, Exception)
