import pytest
from pydantic import create_model

from griptape.artifacts import BaseArtifact, ModelArtifact


class TestModelArtifact:
    @pytest.fixture()
    def model_artifact(self):
        return ModelArtifact(
            value=create_model("ModelArtifact", value=(str, ...))(value="foo"),
        )

    def test_to_text(self, model_artifact: ModelArtifact):
        assert model_artifact.to_text() == '{"value":"foo"}'

    def test_to_dict(self, model_artifact: ModelArtifact):
        generic_dict = model_artifact.to_dict()

        assert generic_dict["value"] == {"value": "foo"}

    def test_deserialization(self, model_artifact):
        artifact_dict = model_artifact.to_dict()
        model = BaseArtifact.from_dict(artifact_dict)
        assert isinstance(model, ModelArtifact)
