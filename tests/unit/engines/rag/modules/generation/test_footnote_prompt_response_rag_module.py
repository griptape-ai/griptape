import pytest

from griptape.artifacts import TextArtifact
from griptape.common import Reference
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import FootnotePromptResponseRagModule
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestFootnotePromptResponseRagModule:
    @pytest.fixture()
    def module(self):
        return FootnotePromptResponseRagModule(prompt_driver=MockPromptDriver())

    def test_run(self, module):
        assert module.run(RagContext(query="test")).output.value == "mock output"

    def test_prompt(self, module):
        system_message = module.default_system_template_generator(
            RagContext(query="test", before_query=["*RULESET*", "*META*"]),
            artifacts=[
                TextArtifact("*TEXT SEGMENT 1*", reference=Reference(title="source 1")),
                TextArtifact("*TEXT SEGMENT 2*", reference=Reference(title="source 2")),
                TextArtifact("*TEXT SEGMENT 3*"),
            ],
        )

        assert "*RULESET*" in system_message
        assert "*META*" in system_message
        assert "*TEXT SEGMENT 1*" in system_message
        assert "*TEXT SEGMENT 2*" in system_message
        assert "*TEXT SEGMENT 3*" in system_message
        assert "source 1" in system_message
        assert "source 2" in system_message
