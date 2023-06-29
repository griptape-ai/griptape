import pytest

from griptape.artifacts import TextArtifact
from griptape.engines import PromptSummaryEngine
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestPromptSummaryEngine:
    @pytest.fixture
    def engine(self):
        return PromptSummaryEngine(
            prompt_driver=MockPromptDriver()
        )

    def test_summarize_text(self, engine):
        assert engine.summarize_text("foobar") == "mock output"

    def test_summarize_artifacts(self, engine):
        assert engine.summarize_artifacts([TextArtifact("foobar")]).value == "mock output"
