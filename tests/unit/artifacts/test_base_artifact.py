from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact


class TestBaseArtifact:
    def test_text_artifact_from_dict(self):
        dict_value = {"type": "TextArtifact", "value": "foobar"}
        artifact = BaseArtifact.from_dict(dict_value)

        assert isinstance(artifact, TextArtifact)
        assert artifact.to_text() == "foobar"

    def test_error_artifact_from_dict(self):
        dict_value = {"type": "ErrorArtifact", "value": "foobar"}
        artifact = BaseArtifact.from_dict(dict_value)

        assert isinstance(artifact, ErrorArtifact)
        assert artifact.to_text() == "foobar"

    def test_unsupported_from_dict(self):
        dict_value = {"type": "foo", "value": "foobar"}

        try:
            BaseArtifact.from_dict(dict_value)
            assert False
        except ValueError:
            assert True
