from unittest.mock import Mock

import pytest

from griptape.artifacts import BaseArtifact, UrlArtifact


class TestUrlArtifact:
    @pytest.fixture()
    def url_artifact(self):
        return UrlArtifact(
            value="some url",
        )

    @pytest.fixture(autouse=True)
    def mock_get(self, mocker):
        mock_response = Mock(content=b"some binary data", status_code=200)

        return mocker.patch("requests.get", return_value=mock_response)

    def test_to_text(self, url_artifact: UrlArtifact):
        assert url_artifact.to_text() == "some url"

    def test_to_dict(self, url_artifact: UrlArtifact):
        image_dict = url_artifact.to_dict()

        assert image_dict["value"] == "some url"

    def test_deserialization(self, url_artifact):
        artifact_dict = url_artifact.to_dict()
        deserialized_artifact = BaseArtifact.from_dict(artifact_dict)

        assert isinstance(deserialized_artifact, UrlArtifact)

        assert deserialized_artifact.value == "some url"

    @pytest.mark.parametrize(
        "headers",
        [
            None,
            {},
            {"Authorization": "Bearer some_token"},
        ],
    )
    def test_to_bytes(self, url_artifact, headers):
        assert url_artifact.to_bytes(headers=headers) == b"some binary data"
