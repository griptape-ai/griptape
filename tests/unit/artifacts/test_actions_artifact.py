from griptape.artifacts import ActionsArtifact


class TestActionsArtifact:
    def test___add__(self):
        assert (ActionsArtifact("foo") + ActionsArtifact("bar")).value == "foobar"
