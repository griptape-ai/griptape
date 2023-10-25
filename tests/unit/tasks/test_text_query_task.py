import pytest
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines import VectorQueryEngine
from griptape.structures import Agent
from griptape.tasks import TextQueryTask
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestTextQueryTask:
    @pytest.fixture
    def task(self):
        return TextQueryTask(
            "test",
            query_engine=VectorQueryEngine(
                vector_store_driver=LocalVectorStoreDriver(
                    embedding_driver=MockEmbeddingDriver()
                ),
                prompt_driver=MockPromptDriver(),
            ),
        )

    def test_run(self, task):
        agent = Agent()

        agent.add_task(task)

        assert task.run().to_text() == "mock output"

    def test_context_propagation(self, task):
        task.input_template = "{{ test }}"
        task.context = {"test": "test value"}

        Agent().add_task(task)

        assert task.input.to_text() == "test value"

    def test_load(self, task):
        artifact = task.load("foobar baz", namespace="test")[0]

        assert (
            list(task.query_engine.vector_store_driver.entries.values())[
                0
            ].meta["artifact"]
            == artifact.to_json()
        )
