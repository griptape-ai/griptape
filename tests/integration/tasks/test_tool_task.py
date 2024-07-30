import pytest

from tests.utils.structure_tester import StructureTester


class TestToolTask:
    @pytest.fixture(
        autouse=True, params=StructureTester.TOOL_TASK_CAPABLE_PROMPT_DRIVERS, ids=StructureTester.prompt_driver_id_fn
    )
    def structure_tester(self, request):
        from griptape.structures import Agent
        from griptape.tasks import ToolTask
        from griptape.tools import Calculator

        return StructureTester(
            Agent(tasks=[ToolTask(tool=Calculator())], conversation_memory=None, prompt_driver=request.param)
        )

    def test_tool_task(self, structure_tester):
        structure_tester.run("What is 7 times 3 divided by 5 plus 10.")
