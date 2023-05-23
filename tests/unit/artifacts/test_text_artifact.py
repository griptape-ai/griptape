from griptape.artifacts import TextArtifact
from griptape.tokenizers import TiktokenTokenizer
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestTextArtifact:
    def test___add__(self):
        assert (TextArtifact("foo") + TextArtifact("bar")).value == "foobar"
        
    def test_embedding(self):
        assert TextArtifact("foobar").embedding(MockEmbeddingDriver()) == [0, 1]

    def test_to_text(self):
        assert TextArtifact("foobar").to_text() == "foobar"

    def test_token_count(self):
        assert TextArtifact("foobarbaz").token_count(TiktokenTokenizer()) == 2

    def test_to_dict(self):
        assert TextArtifact("foobar").to_dict()["value"] == "foobar"
