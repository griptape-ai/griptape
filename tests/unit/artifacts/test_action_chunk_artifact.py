from griptape.artifacts import ActionChunkArtifact, TextArtifact


class TestActionChunkArtifact:
    def test___add__(self):
        artifact_1 = ActionChunkArtifact("foo", tag="bar", name="baz", path="qux", partial_input="quux", index=1)
        artifact_2 = ActionChunkArtifact("bar", tag="baz", name="qux", path="quux", partial_input="quuz", index=2)
        added_artifact = artifact_1 + artifact_2
        assert added_artifact.value == "foobar"
        assert added_artifact.tag == "barbaz"
        assert added_artifact.name == "bazqux"
        assert added_artifact.path == "quxquux"
        assert added_artifact.partial_input == "quuxquuz"
        assert added_artifact.index == 1

        artifact_3 = TextArtifact("baz")
        added_artifact = artifact_1 + artifact_3
        assert added_artifact.value == "foobaz"
        assert added_artifact.tag == "bar"
        assert added_artifact.name == "baz"
        assert added_artifact.path == "qux"
        assert added_artifact.partial_input == "quux"
        assert added_artifact.index == 1
