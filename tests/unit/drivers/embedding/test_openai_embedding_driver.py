import pytest
from griptape.drivers import OpenAiEmbeddingDriver
from griptape.tokenizers import OpenAiTokenizer


class TestOpenAiEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_openai(self, mocker):
        fake_response = {"data": [{"embedding": [0, 1, 0]}]}

        return mocker.patch(
            "openai.Embedding.create", return_value=fake_response
        )

    def test_init(self):
        assert OpenAiEmbeddingDriver()

    def test_try_embed_string(self):
        assert OpenAiEmbeddingDriver().try_embed_string("foobar") == [0, 1, 0]

    def test_try_embed_string_with_long_string(self):
        assert OpenAiEmbeddingDriver().try_embed_string(
            " ".join(["foobar"] * 5000)
        ) == [0, 1, 0]

    @pytest.mark.parametrize("model", OpenAiTokenizer.EMBEDDING_MODELS)
    def test_try_embed_string_replaces_newlines_in_older_ada_models(
        self, model, mock_openai
    ):
        OpenAiEmbeddingDriver(model=model).try_embed_string("foo\nbar")
        assert (
            mock_openai.call_args.kwargs["input"] == "foo bar"
            if model.endswith("001")
            else "foo\nbar"
        )

    def test_embed_chunk(self):
        assert OpenAiEmbeddingDriver().embed_chunk("foobar") == [0, 1, 0]
        assert OpenAiEmbeddingDriver().embed_chunk([1, 2, 3]) == [0, 1, 0]

    def test_embed_long_string(self):
        assert OpenAiEmbeddingDriver().embed_long_string(
            " ".join(["foobar"] * 5000)
        ) == [0, 1, 0]
