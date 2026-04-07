from griptape.artifacts import ImageUrlArtifact


class TestImageUrlArtifact:
    def test_init(self):
        assert ImageUrlArtifact(
            value="some url",
        )
