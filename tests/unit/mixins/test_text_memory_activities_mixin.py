import pytest
from griptape.artifacts import TextArtifact, CsvRowArtifact
from tests.mocks.mock_text_memory_processor import MockTextMemoryProcessor


class TestTextMemoryActivitiesMixin:
    @pytest.fixture(autouse=True)
    def mock_griptape(self, mocker):
        mocker.patch(
            "griptape.engines.VectorQueryEngine.query",
            return_value=TextArtifact("foobar")
        )

        mocker.patch(
            "griptape.engines.PromptSummaryEngine.summarize_artifacts",
            return_value=TextArtifact("foobar summary")
        )

        mocker.patch(
            "griptape.engines.CsvExtractionEngine.extract",
            return_value=[CsvRowArtifact({"foo": "bar"})]
        )

    @pytest.fixture
    def memory_processor(self):
        return MockTextMemoryProcessor()

    def test_summarize(self, memory_processor):
        assert memory_processor.summarize(
            {"values": {"query": "foobar", "memory_name": memory_processor.memory.name, "artifact_namespace": "foo"}}
        ).value == "foobar summary"

    def test_query(self, memory_processor):
        assert memory_processor.search(
            {"values": {"query": "foobar", "memory_name": memory_processor.memory.name, "artifact_namespace": "foo"}}
        ).value == "foobar"
