from tests.utils.structure_runner import StructureRunner
import pytest


class TestPromptTask:
    @pytest.fixture(
        autouse=True, params=StructureRunner.PROMPT_TASK_CAPABLE_PROMPT_DRIVERS, ids=StructureRunner.prompt_driver_id_fn
    )
    def structure_runner(self, request):
        from griptape.structures import Agent

        return StructureRunner(Agent(conversation_memory=None, prompt_driver=request.param))

    def test_prompt_task(self, structure_runner):
        structure_runner.run_structure("Write a haiku about pirates.")
