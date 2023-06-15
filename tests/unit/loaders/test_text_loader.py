import pytest
from griptape.loaders.text_loader import TextLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.unit.chunkers.utils import gen_paragraph

MAX_TOKENS = 50


class TestTextLoader:
    @pytest.fixture
    def loader(self):
        return TextLoader(
            embedding_driver=MockEmbeddingDriver(),
            max_tokens=MAX_TOKENS
        )

    def test_load(self, loader):
        text = gen_paragraph(MAX_TOKENS * 2, loader.tokenizer, " ")
        artifacts = loader.load(text)

        assert len(artifacts) == 3
        assert artifacts[0].value.startswith("foo-0 foo-1")
        assert artifacts[0].embedding == [0, 1]

    def test_load_collection(self, loader):
        artifacts = loader.load_collection(["bar", "bat"])

        assert list(artifacts.keys()) == [
            "fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9",
            "ca5bcec12f716f44d9745d349cc80422f0d14cbab09329caf533bef7c2d952eb"
        ]
        assert [a.value for artifact_list in artifacts.values() for a in artifact_list] == ["bar", "bat"]
