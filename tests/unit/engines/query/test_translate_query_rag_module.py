from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import TranslateQueryRagModule
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestTranslateQueryRagModule:
    def test_run(self):
        module = TranslateQueryRagModule(prompt_driver=MockPromptDriver(), language="english")

        assert module.run(RagContext(query="foo")).query == "mock output"
