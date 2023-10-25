import pytest
from griptape.drivers import AzureOpenAiEmbeddingDriver


class TestAzureOpenAiEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_openai(self, mocker):
        fake_response = {"data": [{"embedding": [0, 1, 0]}]}

        mocker.patch("openai.Embedding.create", return_value=fake_response)

    @pytest.fixture
    def driver(self):
        return AzureOpenAiEmbeddingDriver(
            api_base="foobar", model="gpt-4", deployment_id="foobar"
        )

    def test_init(self, driver):
        assert driver

    def test_try_embed_string(self, driver):
        assert driver.try_embed_string("foobar") == [0, 1, 0]

    def test_embed_chunk(self, driver):
        assert driver.embed_chunk("foobar") == [0, 1, 0]
        assert driver.embed_chunk([1, 2, 3]) == [0, 1, 0]

    def test_embed_long_string(self, driver):
        assert driver.embed_long_string("foobar" * 5000) == [0, 1, 0]
