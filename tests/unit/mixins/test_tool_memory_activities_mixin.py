import pytest
from griptape.artifacts import TextArtifact
from tests.mocks.mock_text_memory_processor import MockToolMemoryProcessor


class TestToolMemoryActivitiesMixin:
    @pytest.fixture
    def processor(self):
        return MockToolMemoryProcessor()

    def test_summarize(self, processor):
        processor.memory.store_artifact("foo", TextArtifact("test"))

        assert (
            processor.summarize(
                {
                    "values": {
                        "memory_name": processor.memory.name,
                        "artifact_namespace": "foo",
                    }
                }
            ).value
            == "mock output"
        )

    def test_query(self, processor):
        processor.memory.store_artifact("foo", TextArtifact("test"))

        assert (
            processor.query(
                {
                    "values": {
                        "query": "foobar",
                        "memory_name": processor.memory.name,
                        "artifact_namespace": "foo",
                    }
                }
            ).value
            == "mock output"
        )
