import pytest

from griptape.artifacts import TextArtifact
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import CitationPromptResponseRagModule
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestCitationPromptResponseRagModule:
    @pytest.fixture
    def module(self):
        return CitationPromptResponseRagModule(prompt_driver=MockPromptDriver())

    def test_run(self, module):
        assert module.run(RagContext(query="test")).output.value == "mock output"

    def test_prompt(self, module):
        system_message = module.default_system_template_generator(
            RagContext(
                query="test",
                text_chunks=[
                    TextArtifact("*TEXT SEGMENT 1*", meta={"source": "source 1"}),
                    TextArtifact("*TEXT SEGMENT 2*", meta={"source": "source 2"}),
                    TextArtifact("*TEXT SEGMENT 3*"),
                ],
                before_query=["*RULESET*", "*META*"],
            )
        )

        assert "*RULESET*" in system_message
        assert "*META*" in system_message
        assert "*TEXT SEGMENT 1*" in system_message
        assert "*TEXT SEGMENT 2*" in system_message
        assert "*TEXT SEGMENT 3*" in system_message
        assert "source 1" in system_message
        assert "source 2" in system_message
