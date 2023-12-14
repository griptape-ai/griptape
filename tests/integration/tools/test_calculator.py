from tests.utils.structure_runner import StructureRunner
from fuzzywuzzy import fuzz
import pytest


class TestCalculator:
    @pytest.fixture(
        autouse=True,
        params=StructureRunner.TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=StructureRunner.prompt_driver_id_fn,
    )
    def structure_runner(self, request):
        from griptape.structures import Agent
        from griptape.tools import Calculator

        return StructureRunner(Agent(tools=[Calculator()], conversation_memory=None, prompt_driver=request.params))

    def test_calculate(self, structure_runner):
        result = structure_runner.run_structure("What is 7 times 3 divided by 5 plus 10.")

        assert fuzz.partial_ratio(str(result["answer"]), "14.2") > 80
