from tests.utils.structure_runner import (
    run_structure,
    OUTPUT_RULESET,
    TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS,
    prompt_driver_id_fn,
)
from fuzzywuzzy import fuzz
import pytest


class TestCalculator:
    @pytest.fixture(
        autouse=True,
        params=TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=prompt_driver_id_fn,
    )
    def agent(self, request):
        from griptape.structures import Agent
        from griptape.tools import Calculator

        return Agent(
            tools=[Calculator()],
            memory=None,
            prompt_driver=request.param,
            rulesets=[OUTPUT_RULESET],
        )

    def test_calculate(self, agent):
        result = run_structure(agent, "What is 7 times 3 divided by 5 plus 10.")

        assert fuzz.partial_ratio(str(result["answer"]), "14.2") > 80
