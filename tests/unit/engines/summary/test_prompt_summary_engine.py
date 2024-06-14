import pytest
from griptape.artifacts import TextArtifact, ListArtifact
from griptape.engines import PromptSummaryEngine
from tests.mocks.mock_prompt_driver import MockPromptDriver
import os

class TestPromptSummaryEngine:
    @pytest.fixture
    def engine(self):
        return PromptSummaryEngine(prompt_driver=MockPromptDriver())

    def test_summarize_text(self, engine):
        assert engine.summarize_text("foobar") == "mock output"

    def test_summarize_artifacts(self, engine):
        assert (
            engine.summarize_artifacts(ListArtifact([TextArtifact("foo"), TextArtifact("bar")])).value == "mock output"
        )
    
    def test_max_token_multiplier_invalid(self, engine):
        engine = PromptSummaryEngine(prompt_driver=MockPromptDriver(), max_token_multiplier=0)
        with pytest.raises(ValueError):
            engine.summarize_text("foobar")

        engine = PromptSummaryEngine(prompt_driver=MockPromptDriver(), max_token_multiplier=100000)
        with pytest.raises(ValueError):
            engine.summarize_text("foobar")
        
    def test_chunked_summary(self, engine):
        engine = PromptSummaryEngine(prompt_driver=MockPromptDriver(), max_token_multiplier=.01)

        def copy_test_resource(resource_path: str):
            file_dir = os.path.dirname(__file__)
            full_path = os.path.join(file_dir, "../../../resources", resource_path)
            full_path = os.path.normpath(full_path)

        assert engine.summarize_text(copy_test_resource("test.txt"))
