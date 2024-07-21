import pytest

from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.utils.defaults import rag_engine
from tests.utils.structure_tester import StructureTester


class TestRagTask:
    @pytest.fixture(
        autouse=True,
        params=StructureTester.TEXT_SUMMARY_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=StructureTester.prompt_driver_id_fn,
    )
    def structure_tester(self, request):
        from griptape.artifacts import TextArtifact
        from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver
        from griptape.structures import Agent
        from griptape.tasks import RagTask

        vector_store_driver = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())
        artifact = TextArtifact("John Doe works as as software engineer at Griptape.")
        rag_engine_instance = rag_engine(MockPromptDriver(), vector_store_driver)

        vector_store_driver.upsert_text_artifact(artifact=artifact)

        agent = Agent(prompt_driver=request.param)
        agent.add_task(RagTask("Respond to the users following query: {{ args[0] }}", rag_engine=rag_engine_instance))

        return StructureTester(agent)

    def test_text_query_task(self, structure_tester):
        structure_tester.run("What is the job role of John Doe?")
