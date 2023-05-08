from griptape.artifacts import TextArtifact
from griptape.tokenizers import TiktokenTokenizer


class TestTextArtifact:
    def test_to_text(self):
        assert TextArtifact("foobar").to_text() == "foobar"

    def test_token_count(self):
        assert TextArtifact("foobarbaz").token_count(TiktokenTokenizer()) == 2

    def test_to_dict(self):
        assert TextArtifact("foobar").to_dict()["value"] == "foobar"
