from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import RelatedQueryGenerationRagModule
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestRelatedQueryGenerationRagModule:
    def test_run(self):
        result = RelatedQueryGenerationRagModule(prompt_driver=MockPromptDriver(), query_count=10).run(
            RagContext(initial_query="test")
        )

        assert len(result) == 10
        assert all(r == "mock output" for r in result)
