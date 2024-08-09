import pytest

from griptape.artifacts import TextArtifact
from griptape.engines import PromptSummaryEngine
from griptape.tools import PromptSummaryClient
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.utils import defaults


class TestPromptSummaryClient:
    @pytest.fixture()
    def tool(self):
        return PromptSummaryClient(
            input_memory=[defaults.text_task_memory("TestMemory")],
            prompt_summary_engine=PromptSummaryEngine(prompt_driver=MockPromptDriver()),
        )

    def test_summarize_artifacts(self, tool):
        tool.input_memory[0].store_artifact("foo", TextArtifact("test"))

        assert (
            tool.summarize(
                {"values": {"summary": {"memory_name": tool.input_memory[0].name, "artifact_namespace": "foo"}}}
            ).value
            == "mock output"
        )

    def test_summarize_content(self, tool):
        assert tool.summarize({"values": {"summary": "test"}}).value == "mock output"
