from unittest.mock import MagicMock

import pytest

from griptape.drivers import GoogleEmbeddingDriver


class TestGoogleEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_genai(self, mocker):
        mock_embed_content = mocker.patch("google.generativeai.embed_content")

        mock_value = MagicMock()
        value = {"embedding": [0, 1, 0]}
        mock_value.__getitem__.side_effect = value.__getitem__
        mock_embed_content.return_value = mock_value

        return mock_embed_content

    def test_init(self):
        assert GoogleEmbeddingDriver()

    def test_try_embed_chunk(self):
        assert GoogleEmbeddingDriver().try_embed_chunk("foobar") == [0, 1, 0]
