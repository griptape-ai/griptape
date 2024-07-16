import pytest

from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import PromptResponseRagModule
from griptape.engines.rag.stages import ResponseRagStage
from griptape.structures import Agent
from griptape.tasks import RagTask
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestRagTask:
    @pytest.fixture()
    def task(self):
        return RagTask(
            input="test",
            rag_engine=RagEngine(
                response_stage=ResponseRagStage(
                    response_module=PromptResponseRagModule(prompt_driver=MockPromptDriver())
                )
            ),
        )

    def test_run(self, task):
        agent = Agent()

        agent.add_task(task)

        assert task.run().to_text() == "mock output"

    def test_context_propagation(self, task):
        task._input = "{{ test }}"
        task.context = {"test": "test value"}

        Agent().add_task(task)

        assert task.input.to_text() == "test value"
