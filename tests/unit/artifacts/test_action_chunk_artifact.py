import pytest
from griptape.artifacts import ActionChunkArtifact, TextArtifact


class TestActionChunkArtifact:
    def test___add__(self):
        artifact_1 = ActionChunkArtifact(
            value=ActionChunkArtifact.ActionChunk(tag="foo", name="bar", path="baz", input="quux", index=1)
        )
        artifact_2 = ActionChunkArtifact(
            value=ActionChunkArtifact.ActionChunk(tag="bar", name="baz", path="qux", input="quuz", index=1)
        )
        added_artifact = artifact_1 + artifact_2

        assert added_artifact.value == ActionChunkArtifact.ActionChunk(
            tag="foobar", name="barbaz", path="bazqux", input="quuxquuz", index=1
        )

    def test__add__different_index(self):
        artifact_1 = ActionChunkArtifact(
            value=ActionChunkArtifact.ActionChunk(tag="foo", name="bar", path="baz", input="quux", index=1)
        )
        artifact_2 = ActionChunkArtifact(
            value=ActionChunkArtifact.ActionChunk(tag="bar", name="baz", path="qux", input="quuz", index=2)
        )

        with pytest.raises(ValueError):
            artifact_1 += artifact_2

    def test___add__not_implemented(self):
        artifact_1 = ActionChunkArtifact(
            value=ActionChunkArtifact.ActionChunk(tag="foo", name="bar", path="baz", input="quux", index=1)
        )

        with pytest.raises(NotImplementedError):
            artifact_1 += TextArtifact("foo")
