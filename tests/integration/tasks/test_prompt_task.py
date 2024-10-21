import pytest

from tests.utils.structure_tester import StructureTester


class TestPromptTask:
    @pytest.fixture(
        autouse=True,
        params=StructureTester.PROMPT_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=StructureTester.generate_prompt_driver_id,
    )
    def structure_tester(self, request):
        from griptape.structures import Agent

        return StructureTester(Agent(conversation_memory=None, prompt_driver=request.param))

    def test_prompt_task(self, structure_tester):
        structure_tester.run("Write a poem about pirates.")
