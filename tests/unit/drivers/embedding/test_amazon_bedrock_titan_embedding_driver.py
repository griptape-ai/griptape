from contextlib import nullcontext
from unittest import mock

import pytest

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers.embedding.amazon_bedrock import AmazonBedrockTitanEmbeddingDriver


class TestAmazonBedrockTitanEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def _mock_session(self, mocker):
        fake_embeddings = '{"embedding": [0, 1, 0]}'

        mock_session_class = mocker.patch("boto3.Session")

        mock_session_object = mock.Mock()
        mock_client = mock.Mock()
        mock_response = mock.Mock()

        mock_response.get().read.return_value = fake_embeddings
        mock_client.invoke_model.return_value = mock_response
        mock_session_object.client.return_value = mock_client
        mock_session_class.return_value = mock_session_object

    def test_init(self):
        assert AmazonBedrockTitanEmbeddingDriver()

    @pytest.mark.parametrize(
        ("value", "expected_output", "expected_error"),
        [
            ("foobar", [0, 1, 0], nullcontext()),
            (
                TextArtifact("foobar"),
                [0, 1, 0],
                nullcontext(),
            ),
            (
                ImageArtifact(b"foobar", format="jpeg", width=1, height=1),
                [0, 1, 0],
                nullcontext(),
            ),
        ],
    )
    def test_embed(self, value, expected_output, expected_error):
        with expected_error:
            assert AmazonBedrockTitanEmbeddingDriver().embed(value) == expected_output
