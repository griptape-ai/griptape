from griptape.artifacts import CsvRowArtifact
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestCsvRowArtifact:
    def test___add__(self):
        assert (CsvRowArtifact({"test1": "foo"}) + CsvRowArtifact({"test2": "bar"})).value == \
               {"test1": "foo", "test2": "bar"}

    def test_generate_embedding(self):
        assert CsvRowArtifact({"test1": "foo"}).generate_embedding(MockEmbeddingDriver()) == [0, 1]

    def test_to_text(self):
        assert CsvRowArtifact({
            "test1": "foo",
            "test2": 1
        }).to_text() == "foo,1"

    def test_to_dict(self):
        assert CsvRowArtifact({"test1": "foo"}).to_dict()["value"] == {'test1': 'foo'}
