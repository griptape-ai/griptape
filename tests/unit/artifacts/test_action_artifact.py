import pytest
from griptape.artifacts import ActionArtifact, ActionChunkArtifact


class TestActionArtifact:
    def test___add__(self):
        action_artifact_1 = ActionArtifact(value=ActionArtifact.Action(tag="foo", name="bar", path="baz", input={}))
        action_artifact_2 = ActionArtifact(value=ActionArtifact.Action(tag="bar", name="baz", path="qux", input={}))

        with pytest.raises(NotImplementedError):
            action_artifact_1 += action_artifact_2

    def test_from_chunks(self):
        chunks = [
            ActionChunkArtifact(ActionChunkArtifact.ActionChunk(tag="foo", name="bar", path="baz", input="{", index=1)),
            ActionChunkArtifact(
                ActionChunkArtifact.ActionChunk(tag="bar", name="baz", path="qux", input='"foo": "bar"', index=1)
            ),
            ActionChunkArtifact(
                ActionChunkArtifact.ActionChunk(tag="baz", name="qux", path="quux", input="}", index=1)
            ),
        ]

        action_artifact = ActionArtifact.from_chunks(chunks)

        assert action_artifact.value == ActionArtifact.Action(
            tag="foobarbaz", name="barbazqux", path="bazquxquux", input={"foo": "bar"}
        )

    def test_from_chunks_bad_input(self):
        chunks = [
            ActionChunkArtifact(ActionChunkArtifact.ActionChunk(tag="foo", name="bar", path="baz", input="{", index=1)),
            ActionChunkArtifact(
                ActionChunkArtifact.ActionChunk(tag="bar", name="baz", path="qux", input="very very bad", index=1)
            ),
            ActionChunkArtifact(
                ActionChunkArtifact.ActionChunk(tag="baz", name="qux", path="quux", input="}", index=2)
            ),
        ]

        with pytest.raises(ValueError):
            ActionArtifact.from_chunks(chunks)
