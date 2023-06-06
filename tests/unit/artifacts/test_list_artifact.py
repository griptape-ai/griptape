from griptape.artifacts import ListArtifact, BaseArtifact, TextArtifact
from griptape.schemas import ListArtifactSchema


class TestListArtifact:
    def test_to_text(self):
        assert ListArtifact([TextArtifact("foobar")]).to_text() == \
               "Artifact contains multiple values:\nfoobar"

        assert ListArtifact().to_text() == \
               "This artifact is empty"

    def test_to_dict(self):
        assert ListArtifact([TextArtifact("foobar")]).to_dict()["value"][0]["value"] == "foobar"

    def test_serialization(self):
        artifact = ListArtifact([TextArtifact("foobar")])
        artifact_dict = ListArtifactSchema().dump(artifact)

        assert artifact_dict["value"][0]["value"] == "foobar"

    def test_deserialization(self):
        artifact = ListArtifact([TextArtifact("foobar")])
        artifact_dict = ListArtifactSchema().dump(artifact)
        deserialized_artifact: ListArtifact = BaseArtifact.from_dict(artifact_dict)

        assert deserialized_artifact.value[0].value == "foobar"

    def test_from_list(self):
        assert len(ListArtifact.from_list([TextArtifact("foo"), TextArtifact("bar")]).value) == 2
