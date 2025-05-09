from griptape.artifacts import AudioUrlArtifact


class TestAudioUrlArtifact:
    def test_init(self):
        assert AudioUrlArtifact(
            value="some url",
        )
