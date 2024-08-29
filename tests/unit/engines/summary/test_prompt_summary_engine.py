import os
from pathlib import Path

import pytest

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.common import PromptStack
from griptape.engines import PromptSummaryEngine
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestPromptSummaryEngine:
    @pytest.fixture()
    def engine(self):
        return PromptSummaryEngine()

    def test_summarize_text(self, engine):
        assert engine.summarize_text("foobar") == "mock output"

    def test_summarize_artifacts(self, engine):
        assert (
            engine.summarize_artifacts(ListArtifact([TextArtifact("foo"), TextArtifact("bar")])).value == "mock output"
        )

    def test_max_token_multiplier_invalid(self, engine):
        with pytest.raises(ValueError):
            PromptSummaryEngine(max_token_multiplier=0)

        with pytest.raises(ValueError):
            PromptSummaryEngine(max_token_multiplier=10000)

    def test_chunked_summary(self, engine):
        def smaller_input(prompt_stack: PromptStack):
            return prompt_stack.messages[0].content[: (len(prompt_stack.messages[0].content) // 2)]

        engine = PromptSummaryEngine(prompt_driver=MockPromptDriver(mock_output="smaller_input"))

        def copy_test_resource(resource_path: str):
            file_dir = os.path.dirname(__file__)
            full_path = os.path.join(file_dir, "../../../resources", resource_path)
            full_path = os.path.normpath(full_path)
            return Path(full_path).read_text()

        assert engine.summarize_text(copy_test_resource("test.txt") * 50)

    def test_summarize_artifacts_rec_no_artifacts(self, engine):
        with pytest.raises(ValueError):
            engine.summarize_artifacts_rec([])

        output = engine.summarize_artifacts_rec([], "summary")
        assert output.value == "summary"
