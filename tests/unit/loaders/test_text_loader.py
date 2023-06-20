import pytest
from griptape import utils
from griptape.loaders.text_loader import TextLoader
from tests.unit.chunkers.utils import gen_paragraph

MAX_TOKENS = 50


class TestTextLoader:
    @pytest.fixture
    def loader(self):
        return TextLoader(
            max_tokens=MAX_TOKENS
        )

    def test_load(self, loader):
        text = gen_paragraph(MAX_TOKENS * 2, loader.tokenizer, " ")
        artifacts = loader.load(text)

        assert len(artifacts) == 3
        assert artifacts[0].value.startswith("foo-0 foo-1")

    def test_load_collection(self, loader):
        artifacts = loader.load_collection(["bar", "bat"])

        assert list(artifacts.keys()) == [
            utils.str_to_hash("bar"),
            utils.str_to_hash("bat")
        ]
        assert [a.value for artifact_list in artifacts.values() for a in artifact_list] == ["bar", "bat"]
