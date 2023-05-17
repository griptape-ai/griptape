import pytest
from griptape.drivers import OpenAiEmbeddingDriver


class TestOpenAiEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_openai_embedding_create(self, mocker):
        # Create a fake response
        fake_response = {
            "data": [
                {
                    "embedding": [0, 1, 0]
                }
            ]
        }

        mocker.patch('openai.Embedding.create', return_value=fake_response)

    def test_init(self):
        assert OpenAiEmbeddingDriver()

    def test_try_embed_string(self):
        assert OpenAiEmbeddingDriver().try_embed_string("foobar") == [0, 1, 0]

    def test_embed_chunk(self):
        assert OpenAiEmbeddingDriver().embed_chunk("foobar") == [0, 1, 0]
        assert OpenAiEmbeddingDriver().embed_chunk([1,2,3]) == [0, 1, 0]

    def test_embed_long_string(self):
        assert OpenAiEmbeddingDriver().embed_long_string("foobar" * 5000) == [0, 1, 0]
