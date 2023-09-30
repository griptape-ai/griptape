import pytest
from griptape.drivers import SentenceTransformersEmbeddingDriver
import numpy as np

MOCK_EMBEDDING = [0,1,0]

class TestSentenceTransformerEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_sentence_transformers(self, mocker):
        """Mock the SentenceTransformers library's encode method."""
        # Shape is (batch_size, embedding_size)
        fake_response = np.array([MOCK_EMBEDDING])

        return mocker.patch("sentence_transformers.SentenceTransformer.encode", return_value=fake_response)

    def test_init(self):
        """Test that the driver can be initialized."""
        assert SentenceTransformersEmbeddingDriver()

    def test_try_embed_string(self):
        """Test that the driver can embed a short string."""
        assert SentenceTransformersEmbeddingDriver().try_embed_string("foobar") == MOCK_EMBEDDING

    def test_try_embed_string_with_long_string(self):
        """Test that the driver can embed a long string."""
        assert SentenceTransformersEmbeddingDriver().try_embed_string(" ".join(["foobar"] * 5000)) == MOCK_EMBEDDING

