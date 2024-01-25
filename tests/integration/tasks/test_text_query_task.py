from tests.utils.structure_tester import StructureTester
import pytest


class TestTextQueryTask:
    @pytest.fixture(
        autouse=True,
        params=StructureTester.TEXT_SUMMARY_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=StructureTester.prompt_driver_id_fn,
    )
    def structure_tester(self, request):
        from griptape.structures import Agent
        from griptape.tasks import TextQueryTask
        from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver
        from griptape.engines import VectorQueryEngine
        from griptape.artifacts import TextArtifact

        vector_store_driver = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

        artifact = TextArtifact("John Doe works as as software engineer at Griptape.")

        vector_query_engine = VectorQueryEngine(prompt_driver=request.param, vector_store_driver=vector_store_driver)
        vector_query_engine.upsert_text_artifact(artifact=artifact)

        agent = Agent(prompt_driver=request.param)
        agent.add_task(
            TextQueryTask("Respond to the users following query: {{ args[0] }}", query_engine=vector_query_engine)
        )

        return StructureTester(agent)

    def test_text_query_task(self, structure_tester):
        structure_tester.run("What is the job role of John Doe?")
