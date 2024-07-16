import pytest

from griptape.artifacts.error_artifact import ErrorArtifact
from griptape.loaders import WebLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

MAX_TOKENS = 50


class TestWebLoader:
    @pytest.fixture(autouse=True)
    def _mock_trafilatura_fetch_url(self, mocker):
        mocker.patch("trafilatura.fetch_url", return_value="<html>foobar</html>")

    @pytest.fixture()
    def loader(self):
        return WebLoader(max_tokens=MAX_TOKENS, embedding_driver=MockEmbeddingDriver())

    def test_load(self, loader):
        artifacts = loader.load("https://github.com/griptape-ai/griptape")

        assert len(artifacts) == 1
        assert "foobar" in artifacts[0].value.lower()

        assert artifacts[0].embedding == [0, 1]

    def test_load_exception(self, mocker, loader):
        mocker.patch("trafilatura.fetch_url", side_effect=Exception("error"))
        source = "https://github.com/griptape-ai/griptape"
        artifact = loader.load(source)

        assert isinstance(artifact, ErrorArtifact)
        assert f"Error loading from source: {source}" == artifact.value

    def test_load_collection(self, loader):
        artifacts = loader.load_collection(
            ["https://github.com/griptape-ai/griptape", "https://github.com/griptape-ai/griptape-docs"]
        )

        assert list(artifacts.keys()) == [
            loader.to_key("https://github.com/griptape-ai/griptape"),
            loader.to_key("https://github.com/griptape-ai/griptape-docs"),
        ]
        assert "foobar" in [a.value for artifact_list in artifacts.values() for a in artifact_list][0].lower()

        assert list(artifacts.values())[0][0].embedding == [0, 1]

    def test_empty_page_string_response(self, loader, mocker):
        mocker.patch("trafilatura.extract", return_value="")

        artifact = loader.load("https://example.com/")
        assert isinstance(artifact, ErrorArtifact)
        assert str(artifact.exception) == "can't extract page"

    def test_empty_page_none_response(self, loader, mocker):
        mocker.patch("trafilatura.extract", return_value=None)

        artifact = loader.load("https://example.com/")
        assert isinstance(artifact, ErrorArtifact)
        assert str(artifact.exception) == "can't extract page"
