import pytest

from griptape.artifacts import TextArtifact
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import TextChunksResponseRagModule


class TestTextChunksResponseRagModule:
    @pytest.fixture()
    def module(self):
        return TextChunksResponseRagModule()

    def test_run(self, module):
        text_chunks = [TextArtifact("foo"), TextArtifact("bar")]

        assert module.run(RagContext(query="test", text_chunks=text_chunks)).output.value == text_chunks
