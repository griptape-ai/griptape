import pytest

from tests.utils.structure_tester import StructureTester


class TestCalculator:
    @pytest.fixture(
        autouse=True,
        params=StructureTester.TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=StructureTester.prompt_driver_id_fn,
    )
    def structure_tester(self, request):
        from griptape.structures import Agent
        from griptape.tools import Calculator

        return StructureTester(Agent(tools=[Calculator()], conversation_memory=None, prompt_driver=request.param))

    def test_calculate(self, structure_tester):
        structure_tester.run("What is 7 times 3 divided by 5 plus 10.")
