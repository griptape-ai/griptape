import os
from pathlib import Path
import pytest
from griptape import utils
from griptape.loaders.text_loader import TextLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.unit.chunkers.utils import gen_paragraph

MAX_TOKENS = 50


class TestTextLoader:
    @pytest.fixture
    def loader(self):
        return TextLoader(
            max_tokens=MAX_TOKENS, embedding_driver=MockEmbeddingDriver()
        )

    def test_load_with_str(self, loader):
        text = gen_paragraph(MAX_TOKENS * 2, loader.tokenizer, " ")
        artifacts = loader.load(text)

        assert len(artifacts) == 3
        assert artifacts[0].value.startswith("foo-0 foo-1")

        assert artifacts[0].embedding == [0, 1]

    def test_load_with_path(self, loader):
        path = Path(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                "../../resources/test.txt",
            )
        )

        artifacts = loader.load(path)

        assert len(artifacts) == 39
        assert artifacts[0].value.startswith("foobar foobar foobar")

        assert artifacts[0].embedding == [0, 1]

    def test_load_collection_with_strings(self, loader):
        artifacts = loader.load_collection(["bar", "bat"])

        assert list(artifacts.keys()) == [
            utils.str_to_hash("bar"),
            utils.str_to_hash("bat"),
        ]
        assert [
            a.value
            for artifact_list in artifacts.values()
            for a in artifact_list
        ] == ["bar", "bat"]

        assert list(artifacts.values())[0][0].embedding == [0, 1]

    def test_load_collection_with_path(self, loader):
        path = Path(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                "../../resources/test.txt",
            )
        )
        artifacts = loader.load_collection([path])

        key = utils.str_to_hash(str(path))

        assert list(artifacts.keys())[0] == key
        assert len(artifacts[key]) == 39

        assert list(artifacts.values())[0][0].embedding == [0, 1]
