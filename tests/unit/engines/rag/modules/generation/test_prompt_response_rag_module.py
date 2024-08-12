import pytest

from griptape.artifacts import TextArtifact
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import PromptResponseRagModule
from griptape.rules import Rule, Ruleset
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestPromptResponseRagModule:
    @pytest.fixture()
    def module(self):
        return PromptResponseRagModule(
            prompt_driver=MockPromptDriver(),
            rulesets=[Ruleset(name="test", rules=[Rule("*RULESET*")])],
            metadata="*META*",
        )

    def test_run(self, module):
        assert module.run(RagContext(query="test")).value == "mock output"

    def test_prompt(self, module):
        system_message = module.default_system_template_generator(
            RagContext(query="test"),
            artifacts=[TextArtifact("*TEXT SEGMENT 1*"), TextArtifact("*TEXT SEGMENT 2*")],
        )

        assert "*RULESET*" in system_message
        assert "*META*" in system_message
        assert "*TEXT SEGMENT 1*" in system_message
        assert "*TEXT SEGMENT 2*" in system_message
