from griptape.artifacts import TextArtifact
from griptape.common import Reference
from griptape.engines.rag import RagContext


class TestRagContext:
    def test_get_references(self):
        reference1 = Reference(title="foo")
        reference2 = Reference(title="bar")
        context = RagContext(
            query="foo",
            text_chunks=[
                TextArtifact("foo", reference=reference1),
                TextArtifact("foo", reference=reference1),
                TextArtifact("foo", reference=reference2),
            ]
        )
        references = context.get_references()

        assert len(references) == 2
        assert references[0].id == reference1.id
        assert references[1].id == reference2.id
