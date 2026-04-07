import pytest

from griptape.loaders import WebLoader

MAX_TOKENS = 50


class TestWebLoader:
    @pytest.fixture(autouse=True)
    def _mock_trafilatura_fetch_url(self, mocker):
        mocker.patch("trafilatura.fetch_url", return_value="<html>foobar</html>")

    @pytest.fixture()
    def loader(self):
        return WebLoader()

    def test_load(self, loader):
        artifact = loader.load("https://github.com/griptape-ai/griptape")

        assert "foobar" in artifact.value.lower()

    def test_load_exception(self, mocker, loader):
        mocker.patch("trafilatura.fetch_url", side_effect=Exception("error"))
        source = "https://github.com/griptape-ai/griptape"
        with pytest.raises(Exception, match="error"):
            loader.load(source)

    def test_load_collection(self, loader):
        artifacts = loader.load_collection(
            ["https://github.com/griptape-ai/griptape", "https://github.com/griptape-ai/griptape-docs"]
        )

        assert list(artifacts.keys()) == [
            loader.to_key("https://github.com/griptape-ai/griptape"),
            loader.to_key("https://github.com/griptape-ai/griptape-docs"),
        ]
        assert "foobar" in [a.value for a in artifacts.values()]

    def test_empty_page_string_response(self, loader, mocker):
        mocker.patch("trafilatura.extract", return_value="")

        with pytest.raises(Exception, match="can't extract page"):
            loader.load("https://example.com/")

    def test_empty_page_none_response(self, loader, mocker):
        mocker.patch("trafilatura.extract", return_value=None)

        with pytest.raises(Exception, match="can't extract page"):
            loader.load("https://example.com/")
