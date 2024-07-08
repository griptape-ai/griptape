import pytest

from griptape.artifacts import TextArtifact
from griptape.common import Reference
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import PromptResponseRagModule
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestPromptResponseRagModule:
    @pytest.fixture
    def module(self):
        return PromptResponseRagModule(prompt_driver=MockPromptDriver())

    def test_run(self, module):
        assert module.run(RagContext(query="test")).output.value == "mock output"

    def test_prompt(self, module):
        system_message = module.default_system_template_generator(
            RagContext(query="test", before_query=["*RULESET*", "*META*"], after_query=[]),
            artifacts=[TextArtifact("*TEXT SEGMENT 1*"), TextArtifact("*TEXT SEGMENT 2*")],
        )

        assert "*RULESET*" in system_message
        assert "*META*" in system_message
        assert "*TEXT SEGMENT 1*" in system_message
        assert "*TEXT SEGMENT 2*" in system_message

    def test_references_from_artifacts(self, module):
        reference1 = Reference(title="foo")
        reference2 = Reference(title="bar")
        artifacts = [
            TextArtifact("foo", reference=reference1),
            TextArtifact("foo", reference=reference1),
            TextArtifact("foo"),
            TextArtifact("foo", reference=reference2),
        ]
        references = module.references_from_artifacts(artifacts)

        assert len(references) == 2
        assert references[0].id == reference1.id
        assert references[1].id == reference2.id
