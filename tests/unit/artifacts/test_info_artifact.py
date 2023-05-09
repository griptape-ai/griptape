from griptape.artifacts import InfoArtifact
from griptape.tokenizers import TiktokenTokenizer


class TestInfoArtifact:
    def test_to_text(self):
        assert InfoArtifact("foobar").to_text() == "foobar"

    def test_token_count(self):
        assert InfoArtifact("foobarbaz").token_count(TiktokenTokenizer()) == 2

    def test_to_dict(self):
        assert InfoArtifact("foobar").to_dict()["value"] == "foobar"
